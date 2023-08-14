import mysql.connector
from server.config import MYSQL_CONFIG


def fetch_points():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    points = []
    query = """
		SELECT id, x, y, z, rx, ry, rz
		FROM point
	"""
    cursor.execute(query)
    for res in cursor:
        points.append(res)

    cursor.close()
    cnx.close()

    return points


def fetch_lines():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    lines = []
    query = """
		SELECT id, a, b, length, rlength
		FROM line
	"""
    cursor.execute(query)
    for line in cursor:
        lines.append((line[0], line[1], line[2], line[3], line[4]))

    cursor.close()
    cnx.close()

    return lines


def fetch_arcs():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()

    arcs = []
    query = """
		SELECT id, radius, cx, cy, cz, rradius, rcx, rcy, rcz
		FROM arc
	"""
    cursor.execute(query)
    for arc in cursor:
        arcs.append(
            (arc[0], arc[1], arc[2], arc[3], arc[4], arc[5], arc[6], arc[7], arc[8])
        )

    cursor.close()
    cnx.close()

    return arcs
