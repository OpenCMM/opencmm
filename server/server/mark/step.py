import numpy as np
from server.mark.line import get_sides, get_side
import mysql.connector
from server.config import get_config, MODEL_PATH
import trimesh


def sort_sides(sides):
    """
    Sort sides by x, y, z
    """
    sorted_sides = []
    for side in sides:
        side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = side
        if x0 < x1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 < y1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 == y1 and z0 < z1:
            sorted_sides.append(side)
        else:
            sorted_sides.append([side_id, model_id, x1, y1, z1, x0, y0, z0, pair_id])
    return sorted_sides


def import_steps(mysql_config: dict, model_id: int):
    sides = get_sides(mysql_config, model_id)
    sorted_sides = sort_sides(sides)

    np_sides = np.array(sorted_sides)
    xy_points = np_sides[:, [2, 3, 5, 6]]
    _unique, _counts = np.unique(xy_points, axis=0, return_counts=True)
    duplicate_xy_points = _unique[_counts > 1]
    # get rows with duplicate xy points from np_sides
    duplicate_xy_points = duplicate_xy_points.tolist()
    duplicate_rows = []
    for duplicate_xy_point in duplicate_xy_points:
        duplicate_rows.append(
            np.argwhere(
                (np_sides[:, [2, 3, 5, 6]] == duplicate_xy_point).all(axis=1)
            ).flatten()
        )

    steps = []
    for idx in duplicate_rows:
        duplicate_sides = np_sides[idx]
        first_side = duplicate_sides[0]
        second_side = duplicate_sides[1]
        # same line, no step
        if first_side[4] == second_side[4]:
            continue
        if first_side[4] != first_side[7]:
            continue
        if second_side[4] != second_side[7]:
            continue
        steps.append(duplicate_sides)

    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO trace (model_id, type, start, end, result) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    import_data = []
    for step in steps:
        step = step.tolist()
        model_id = step[0][1]
        trace_type = "step"
        start = step[0][0]
        end = step[1][0]
        height = abs(step[0][4] - step[1][4])
        import_data.append((model_id, trace_type, start, end, height))

    cursor.executemany(query, import_data)
    cnx.commit()
    cursor.close()


def get_steps(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM trace WHERE model_id = %s AND type = 'step'"
    cursor.execute(query, (model_id,))
    steps = cursor.fetchall()
    cursor.close()
    cnx.close()
    return steps


def create_step_lines(base_side):
    conf = get_config()
    trace_margin = conf["trace"]["margin"]

    x0 = base_side[2]
    y0 = base_side[3]

    x1 = base_side[5]
    y1 = base_side[6]

    vector = np.array([x1 - x0, y1 - y0])
    # one unit vector
    unit_vector = vector / np.linalg.norm(vector)

    start = np.array([x0, y0])
    end = np.array([x1, y1])

    # diagnol vector of unit vector
    diagnol_vector = np.array([-unit_vector[1], unit_vector[0]])

    start0 = start + diagnol_vector * trace_margin + unit_vector * trace_margin
    end0 = end + diagnol_vector * trace_margin - unit_vector * trace_margin

    start1 = start - diagnol_vector * trace_margin + unit_vector * trace_margin
    end1 = end - diagnol_vector * trace_margin - unit_vector * trace_margin

    # round to 3 decimal places
    start0 = [round(x, 3) for x in start0]
    end0 = [round(x, 3) for x in end0]
    start1 = [round(x, 3) for x in start1]
    end1 = [round(x, 3) for x in end1]
    return [[start0, end0], [start1, end1]]


def get_z_value_with_ray_cast(mesh, ray_origin_xy):
    ray_origin = [*ray_origin_xy, 10000]
    ray_directions = np.array([[0, 0, -1]])
    ray_origins = np.array([ray_origin])
    location = mesh.ray.intersects_location(ray_origins, ray_directions)[0][0]
    # get z value
    return location[2]


def to_trace_line_row(trace_id: int, mesh, step_line, z_pair: list, offset: tuple):
    """
    get z value with raycast and create row for trace_line table
    """
    step_line_start = step_line[0]
    step_line_end = step_line[1]
    step_line_start_z = get_z_value_with_ray_cast(mesh, step_line_start)
    step_line_end_z = get_z_value_with_ray_cast(mesh, step_line_end)
    assert step_line_start_z == step_line_end_z
    assert step_line_start_z in z_pair
    # add offset
    step_line_start = [step_line_start[0] + offset[0], step_line_start[1] + offset[1]]
    step_line_end = [step_line_end[0] + offset[0], step_line_end[1] + offset[1]]
    step_line_z = step_line_start_z + offset[2]
    # trace_id, x0, y0, x1, y1, z
    return [trace_id, *step_line_start, *step_line_end, step_line_z]


def create_step_path(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    move_feedrate: float,
    xyz_offset: tuple = (0, 0, 0),
):
    conf = get_config()
    trace_feedrate = conf["trace"]["feedrate"]

    mesh = trimesh.load_mesh(f"{MODEL_PATH}/{stl_filename}")

    path = []
    trace_lines = []
    steps = get_steps(mysql_config, model_id)
    for step in steps:
        trace_id, model_id, trace_type, start, end, height = step
        start_side = get_side(start, mysql_config)
        end_side = get_side(end, mysql_config)
        z_pair = [start_side[4], end_side[4]]

        step_lines = create_step_lines(start_side)
        for step_line in step_lines:
            trace_lines.append(
                to_trace_line_row(trace_id, mesh, step_line, z_pair, xyz_offset)
            )
            path.append(
                "G1 X{} Y{} F{}".format(step_line[0][0], step_line[0][1], move_feedrate)
            )
            path.append(
                "G1 X{} Y{} F{}".format(
                    step_line[1][0], step_line[1][1], trace_feedrate
                )
            )

    return path, trace_lines


def import_trace_lines(mysql_config: dict, trace_lines: list, init_line: int):
    # add line number
    for idx, trace_line in enumerate(trace_lines):
        trace_line.append(init_line + idx * 2)

    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO trace_line (trace_id, x0, y0, x1, y1, z, line) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, trace_lines)
    cnx.commit()
    cursor.close()
    cnx.close()


def get_trace_lines(mysql_config: dict, trace_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM trace_line WHERE trace_id = %s"
    cursor.execute(query, (trace_id,))
    trace_lines = cursor.fetchall()
    cursor.close()
    cnx.close()
    return trace_lines


def delete_trace_lines(mysql_config: dict, trace_id_list: list):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM trace_line WHERE trace_id = %s"
    for trace_id in trace_id_list:
        cursor.execute(query, (trace_id,))
        cnx.commit()
    cursor.close()
    cnx.close()
