import numpy as np
from server.mark.line import get_sides
from .trace import import_traces
import mysql.connector
from server.config import get_config
from server.mark.line import get_side
from .trace import sort_sides


def group_sides_by_pair_id(sides: list):
    """
    Each side has a pair_id. This function groups sides by pair_id.
    """
    sides_by_pair_id = {}
    for side in sides:
        pair_id = side[8]
        if pair_id not in sides_by_pair_id:
            sides_by_pair_id[pair_id] = []
        sides_by_pair_id[pair_id].append(side)
    return sides_by_pair_id.values()


def import_slopes(mysql_config: dict, model_id: int):
    sides = get_sides(mysql_config, model_id)
    np_sides = np.array(sides)
    traces = []

    sides_by_pair_id = group_sides_by_pair_id(sides)
    for pair_sides in sides_by_pair_id:
        slope_pair = None
        # check if z values are the same
        if pair_sides[0][4] != pair_sides[1][4]:
            slope_pair = pair_sides

        if slope_pair is None:
            continue

        # low to high
        if slope_pair[0][4] < slope_pair[1][4]:
            slope_start = slope_pair[0]
            slope_end = slope_pair[1]
        else:
            slope_start = slope_pair[1]
            slope_end = slope_pair[0]

        slope_start0 = np.array(slope_start[2:5])
        slope_start1 = np.array(slope_start[5:8])
        slope_end0 = np.array(slope_end[2:5])
        slope_end1 = np.array(slope_end[5:8])
        slope_start_middle_point = (slope_start0 + slope_start1) / 2
        slope_end_middle_point = (slope_end0 + slope_end1) / 2

        slope_start_data = slope_start.flatten()
        slope_end_data = slope_end.flatten()
        for side in np_sides:
            if (side[2:8] == slope_start_data).all():
                start_side_id = side[0]
            if (side[2:8] == slope_end_data).all():
                end_side_id = side[0]

        angle = get_angle(slope_start_middle_point, slope_end_middle_point)
        traces.append([model_id, "slope", start_side_id, end_side_id, angle])

    if traces:
        import_traces(mysql_config, traces)


def get_angle(start_point: np.ndarray, end_point: np.ndarray):
    # Calculate the vector representing the line
    line_vector = end_point - start_point
    # Calculate the angle between the line vector and the xy plane
    xy_plane_vector = np.array([1.0, 0.0, 0.0])
    angle = np.arccos(
        np.dot(line_vector, xy_plane_vector)
        / (np.linalg.norm(line_vector) * np.linalg.norm(xy_plane_vector))
    )

    # Convert the angle to degrees
    angle_degrees = np.rad2deg(angle)
    # between 0 and 90
    if angle_degrees > 90:
        angle_degrees = 180 - angle_degrees
    return angle_degrees


def get_slopes(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM trace WHERE model_id = %s AND type = 'slope'"
    cursor.execute(query, (model_id,))
    slopes = cursor.fetchall()
    cursor.close()
    cnx.close()
    return slopes


def create_slope_lines(start_side, end_side):
    conf = get_config()
    trace_margin = conf["trace"]["margin"]
    measure_count = conf["trace"]["slope"]["number"]
    slope_lines = []

    start_side = sort_sides([start_side])
    end_side = sort_sides([end_side])

    start_point0 = np.array(start_side[0][2:5])
    start_point1 = np.array(start_side[0][5:8])
    end_point0 = np.array(end_side[0][2:5])
    end_point1 = np.array(end_side[0][5:8])

    point0_to_point1 = start_point1 - start_point0
    point0_to_point1 /= np.linalg.norm(point0_to_point1)

    vector_point0 = (end_point0 - start_point0) / (measure_count + 1)
    vector_point1 = (end_point1 - start_point1) / (measure_count + 1)

    for i in range(1, measure_count + 1):
        point0 = start_point0 + vector_point0 * i + point0_to_point1 * trace_margin
        point1 = start_point1 + vector_point1 * i - point0_to_point1 * trace_margin

        # round to 3 decimal places
        point0 = [round(x, 3) for x in point0]
        point1 = [round(x, 3) for x in point1]
        slope_lines.append([point0, point1])

    return slope_lines


def to_trace_line_row(trace_id: int, slope_line, offset: tuple):
    line0 = slope_line[0]
    line1 = slope_line[1]
    # add offset
    line0 = [line0[0] + offset[0], line0[1] + offset[1]]
    line1 = [line1[0] + offset[0], line1[1] + offset[1]]
    z = slope_line[0][2] + offset[2]
    # trace_id, x0, y0, x1, y1, z
    return [trace_id, *line0, *line1, z]


def create_slope_path(
    mysql_config: dict,
    model_id: int,
    move_feedrate: float,
    xyz_offset: tuple = (0, 0, 0),
):
    conf = get_config()
    trace_feedrate = conf["trace"]["feedrate"]

    path = []
    trace_lines = []
    slopes = get_slopes(mysql_config, model_id)
    for slope in slopes:
        trace_id, model_id, trace_type, start, end, height = slope
        start_side = get_side(start, mysql_config)
        end_side = get_side(end, mysql_config)
        slope_lines = create_slope_lines(start_side, end_side)
        for slope_line in slope_lines:
            trace_lines.append(to_trace_line_row(trace_id, slope_line, xyz_offset))
            path.append(
                "G1 X{} Y{} F{}".format(
                    slope_line[0][0], slope_line[0][1], move_feedrate
                )
            )
            path.append(
                "G1 X{} Y{} F{}".format(
                    slope_line[1][0], slope_line[1][1], trace_feedrate
                )
            )

    return path, trace_lines
