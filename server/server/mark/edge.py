import mysql.connector
from server.config import MODEL_PATH
from .line import get_side
from .arc import get_arc
import math
from .point import ray_cast


def get_direction(x0, y0, x1, y1):
    if y0 == y1:
        return 0
    elif x0 == x1:
        return 1
    else:
        return -1


def get_edges(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM edge WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def get_arc_path(center, xyz, distance):
    cx, cy, cz = center
    x, y, z = xyz
    # Calculate the direction vector from the center to point A
    direction_vector = (x - cx, y - cy, z - cz)

    # Calculate the magnitude of the direction vector
    magnitude = math.sqrt(
        direction_vector[0] ** 2 + direction_vector[1] ** 2 + direction_vector[2] ** 2
    )

    # Normalize the direction vector
    normalized_direction = (
        direction_vector[0] / magnitude,
        direction_vector[1] / magnitude,
        direction_vector[2] / magnitude,
    )

    # Calculate the coordinates of the two points at distance 'distance' from point A
    outside_point = (
        x + distance * normalized_direction[0],
        y + distance * normalized_direction[1],
        z + distance * normalized_direction[2],
    )
    inside_point = (
        x - distance * normalized_direction[0],
        y - distance * normalized_direction[1],
        z - distance * normalized_direction[2],
    )
    # round to 3 decimal places
    outside_point = [round(x, 3) for x in outside_point]
    inside_point = [round(x, 3) for x in inside_point]
    return outside_point, inside_point


def get_edges_by_side_id(side_id: int, mysql_config: dict, process_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "SELECT edge_result.x, edge_result.y, edge_result.z "
        "FROM edge_result INNER JOIN edge ON edge.id = edge_result.edge_id "
        "WHERE edge.side_id = %s AND edge_result.process_id = %s"
    )
    cursor.execute(query, (side_id, process_id))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def to_gcode_row(x, y, feedrate):
    # round to 3 decimal places
    x = round(x, 3)
    y = round(y, 3)
    return f"G1 X{x} Y{y} F{feedrate}"


def add_line_number_from_path(mysql_config: dict, path: list):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    cursor = cnx.cursor()
    update_list = []
    initial_line_number = 4
    for idx, row in enumerate(path):
        edge_id = row[4]
        update_list.append((initial_line_number + idx * 2, edge_id))
    query = "UPDATE edge SET line = %s WHERE id = %s"
    cursor.executemany(query, update_list)
    cnx.commit()
    cursor.close()
    cnx.close()
    return cursor.rowcount


def get_edge_id_from_line_number(mysql_config: dict, model_id: int, line_number: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM edge WHERE model_id = %s AND line = %s"
    cursor.execute(query, (model_id, line_number))
    edge_id = cursor.fetchone()
    cursor.close()
    cnx.close()
    if edge_id:
        return edge_id[0]


def get_edge_path(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    length: float,
    measure_feedrate: float,
    move_feedrate: float,
    xyz_offset: tuple = (0, 0, 0),
):
    path = []
    edges = get_edges(mysql_config, model_id)
    for edge in edges:
        edge_id, model_id, side_id, arc_id, x, y, z, _line = edge
        # add offset
        (x, y, z) = (x + xyz_offset[0], y + xyz_offset[1], z + xyz_offset[2])
        if arc_id is None:
            side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = get_side(
                side_id, mysql_config
            )
            direction = get_direction(x0, y0, x1, y1)
            if direction == 0:
                hit = ray_cast(
                    f"{MODEL_PATH}/{stl_filename}",
                    (x - xyz_offset[0], y + length - xyz_offset[1], 1000),
                )
                py0, py1 = (y - length, y + length) if hit else (y + length, y - length)
                path.append(
                    [
                        to_gcode_row(x, py0, move_feedrate),
                        to_gcode_row(x, py1, measure_feedrate),
                        x,
                        y,
                        edge_id,
                    ]
                )

            elif direction == 1:
                hit = ray_cast(
                    f"{MODEL_PATH}/{stl_filename}",
                    (x + length - xyz_offset[0], y - xyz_offset[1], 1000),
                )
                px0, px1 = (x - length, x + length) if hit else (x + length, x - length)
                path.append(
                    [
                        to_gcode_row(px0, y, move_feedrate),
                        to_gcode_row(px1, y, measure_feedrate),
                        x,
                        y,
                        edge_id,
                    ]
                )
        else:
            assert side_id is None
            arc_id, model_id, radius, cx, cy, cz = get_arc(arc_id, mysql_config)
            # add offset to center
            (cx, cy, cz) = (cx + xyz_offset[0], cy + xyz_offset[1], cz + xyz_offset[2])
            outside_point, inside_point = get_arc_path((cx, cy, cz), (x, y, z), length)
            hit = ray_cast(
                f"{MODEL_PATH}/{stl_filename}",
                (
                    outside_point[0] - xyz_offset[0],
                    outside_point[1] - xyz_offset[1],
                    1000,
                ),
            )
            first, second = (
                (inside_point, outside_point) if hit else (outside_point, inside_point)
            )
            path.append(
                [
                    to_gcode_row(first[0], first[1], move_feedrate),
                    to_gcode_row(second[0], second[1], measure_feedrate),
                    x,
                    y,
                    edge_id,
                ]
            )
    return sorted(path, key=lambda point: (point[2], point[3]))


def generate_gcode(path, program_number: str):
    gcode = ["%", f"O{program_number}", "G90 G54"]
    for row in path:
        gcode.append(row[0])
        gcode.append(row[1])
    return gcode + ["M30", "%"]


def save_gcode(gcode, file_path: str):
    with open(file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")


def delete_edges_with_model_id(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM edge WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    cnx.commit()
    cursor.close()
    cnx.close()


def get_edge_ids_order_by_x_y(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM edge WHERE model_id = %s ORDER BY x,y"
    cursor.execute(query, (model_id,))
    edge_ids = cursor.fetchall()
    cursor.close()
    cnx.close()
    if edge_ids:
        return [x[0] for x in edge_ids]


def import_edge_results(update_list: list, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO edge_result (edge_id, process_id, "
        "x, y, z) VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, update_list)
    cnx.commit()
    cursor.close()
    cnx.close()


def delete_edge_results(mysql_config: dict, process_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM edge_result WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
