import mysql.connector
from server.config import MYSQL_CONFIG
import numpy as np


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
    cursor.close()
    cnx.close()
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
        if current_pair_id != pair_id:
            current_line = [pair_id, line[1], line[2], line[3]]
            current_pair_id = pair_id
        else:
            current_line += [line[4], line[5], line[6]]
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
