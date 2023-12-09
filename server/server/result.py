import mysql.connector
from server.config import MYSQL_CONFIG
import numpy as np
from server.model import get_model_data
from server.mark.slope import get_angle
from server.measure.sensor import sensor_output_diff_to_mm, sensor_output_to_mm


def fetch_edges(model_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		SELECT id, side_id, x, y, z
		FROM edge WHERE model_id = %s
	"""
    cursor.execute(query, (model_id,))
    points = cursor.fetchall()
    cursor.close()
    cnx.close()
    return points


def fetch_edge_result(process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		SELECT id, x, y, z
		FROM edge_result WHERE process_id = %s
	"""
    cursor.execute(query, (process_id,))
    points = cursor.fetchall()
    cursor.close()
    cnx.close()
    return points


def fetch_edge_result_combined(model_id: int, process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
        SELECT edge.id, edge.x, edge.y, edge.z,
        edge_result.x, edge_result.y, edge_result.z
        FROM edge
        LEFT JOIN edge_result ON edge.id = edge_result.edge_id 
        AND edge_result.process_id = %s
        WHERE edge.model_id = %s ORDER BY edge.id
    """
    cursor.execute(
        query,
        (
            process_id,
            model_id,
        ),
    )
    points = cursor.fetchall()
    points = [list(point) for point in points]
    cursor.close()
    cnx.close()

    model_data = get_model_data(model_id)
    offset = model_data[3:6]
    for point in points:
        point[1] = round(offset[0] + point[1], 3)
        point[2] = round(offset[1] + point[2], 3)
        point[3] = round(offset[2] + point[3], 3)
    return points


def fetch_unique_points(process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		SELECT id, x, y, z, distance
		FROM sensor WHERE process_id = %s
	"""
    cursor.execute(query, (process_id,))
    points = cursor.fetchall()
    cursor.close()
    cnx.close()

    np_points = np.array(points)
    # get rows with unique x, y, z
    unique_points = np.unique(np_points[:, 1:4], axis=0)
    unique_points_with_distance = []
    for point in unique_points:
        distance = np_points[
            np.where(
                (np_points[:, 1] == point[0])
                & (np_points[:, 2] == point[1])
                & (np_points[:, 3] == point[2])
            )
        ][0][4]
        unique_points_with_distance.append([point[0], point[1], point[2], distance])
    return unique_points_with_distance


def fetch_mtconnect_points(process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		SELECT id, x, y, z
		FROM mtconnect WHERE process_id = %s
	"""
    cursor.execute(query, (process_id,))
    points = cursor.fetchall()
    cursor.close()
    cnx.close()
    return points


def fetch_pairs(model_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    lines = []
    query = """
        SELECT pair.id, side.x0, side.y0, 
        side.z0, side.x1, side.y1, side.z1 
        FROM `pair` INNER JOIN side ON pair.id = side.pair_id 
        WHERE pair.model_id = %s
	"""
    cursor.execute(query, (model_id,))
    current_pair_id = -1
    current_line = []
    for line in cursor:
        pair_id = line[0]
        xyz = [line[1:4], line[4:7]]
        # sort by x, y
        xyz.sort(key=lambda x: (x[0], x[1]))
        if current_pair_id != pair_id:
            current_line = [pair_id, *xyz[0]]
            current_pair_id = pair_id
        else:
            current_line += list(xyz[0])
            lines.append(current_line)
            current_line = []

    cursor.close()
    cnx.close()

    return lines


def fetch_lines(model_id: int, process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    lines = []
    query = """
		SELECT pair.id, pair.length, pair_result.length
        FROM pair LEFT JOIN pair_result ON pair.id = pair_result.pair_id
        AND pair_result.process_id = %s 
		WHERE pair.model_id = %s
	"""
    cursor.execute(query, (process_id, model_id))
    for line in cursor:
        lines.append((line[0], line[1], line[2]))

    cursor.close()
    cnx.close()
    return lines


def fetch_arcs(model_id: int, process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    arcs = []
    query = """
		SELECT arc.id, arc.radius, 
        arc.cx, arc.cy, arc.cz, arc_result.radius, 
        arc_result.cx, arc_result.cy, arc_result.cz
        FROM arc LEFT JOIN arc_result ON arc.id = arc_result.arc_id 
        AND arc_result.process_id = %s 
        WHERE arc.model_id = %s
	"""
    cursor.execute(query, (process_id, model_id))
    for arc in cursor:
        arcs.append(
            (arc[0], arc[1], arc[2], arc[3], arc[4], arc[5], arc[6], arc[7], arc[8])
        )

    cursor.close()
    cnx.close()
    return arcs


def group_by_trace_id(traces):
    grouped_arr = {}

    for row in traces:
        first_value = row[0]

        if first_value not in grouped_arr:
            grouped_arr[first_value] = []

        group = grouped_arr[first_value]
        group.append(row)

    # Convert the nested dictionary to a list of lists
    return list(grouped_arr.values())


def fetch_step_results(model_id: int, process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    steps = []
    query = """
		SELECT trace.id, trace.start, trace.end,
        trace.result, trace_line.id,
        trace_line_result.id, trace_line_result.distance
        FROM trace_line INNER JOIN trace ON 
        trace_line.trace_id = trace.id 
        LEFT JOIN trace_line_result ON
        trace_line.id = trace_line_result.trace_line_id
        AND trace_line_result.process_id = %s
        WHERE trace.type = 'step' AND trace.model_id = %s
	"""
    cursor.execute(
        query,
        (
            process_id,
            model_id,
        ),
    )
    traces = cursor.fetchall()
    current_trace_id = None
    previous_distance = None
    for trace in traces:
        if current_trace_id != trace[0]:
            previous_distance = trace[6]
            current_trace_id = trace[0]
        else:
            output_diff = abs(trace[6] - previous_distance)
            diff = sensor_output_diff_to_mm(output_diff)
            steps.append((trace[0], trace[3], diff))

    cursor.close()
    cnx.close()
    return steps


def fetch_slope_results(model_id: int, process_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    slopes = []
    query = """
		SELECT trace.id, trace.start, trace.end,
        trace.result, trace_line.id,
        trace_line.x0, trace_line.y0,
        trace_line_result.id, trace_line_result.distance
        FROM trace_line INNER JOIN trace ON 
        trace_line.trace_id = trace.id 
        LEFT JOIN trace_line_result ON
        trace_line.id = trace_line_result.trace_line_id
        AND trace_line_result.process_id = %s
        WHERE trace.type = 'slope' AND trace.model_id = %s
	"""
    cursor.execute(
        query,
        (
            process_id,
            model_id,
        ),
    )
    traces = cursor.fetchall()
    traces = group_by_trace_id(traces)

    for trace in traces:
        angles = []
        previous_point = None
        angle = trace[0][3]
        trace_id = trace[0][0]
        assert len(trace) > 2
        for row in trace:
            z = sensor_output_to_mm(row[8]) + 100
            current_point = np.array([row[5], row[6], z])
            if previous_point is None:
                previous_point = current_point
            else:
                estimated_angle = get_angle(previous_point, current_point)
                angles.append(estimated_angle)
                previous_point = current_point

        average_angle = sum(angles) / len(angles)
        slopes.append((trace_id, angle, average_angle))

    cursor.close()
    cnx.close()
    return slopes
