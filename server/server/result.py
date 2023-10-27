import mysql.connector
from server.config import MYSQL_CONFIG


def fetch_edges(model_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    query = """
		SELECT id, side_id, x, y, z, rx, ry, rz
		FROM edge WHERE model_id = %s
	"""
    cursor.execute(query, (model_id,))
    points = cursor.fetchall()
    cursor.close()
    cnx.close()

    return points


def fetch_lines(model_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    lines = []
    query = """
		SELECT id, length, rlength
		FROM pair WHERE model_id = %s
	"""
    cursor.execute(query, (model_id,))
    for line in cursor:
        lines.append((line[0], line[1], line[2]))

    cursor.close()
    cnx.close()

    return lines


def fetch_arcs(model_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    arcs = []
    query = """
		SELECT id, radius, cx, cy, cz, rradius, rcx, rcy, rcz
		FROM arc WHERE model_id = %s
	"""
    cursor.execute(query, (model_id,))
    for arc in cursor:
        arcs.append(
            (arc[0], arc[1], arc[2], arc[3], arc[4], arc[5], arc[6], arc[7], arc[8])
        )

    cursor.close()
    cnx.close()

    return arcs
