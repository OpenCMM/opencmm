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
		SELECT a, b
		FROM line
	"""
	cursor.execute(query)
	for line in cursor:
		lines.append((line[0], line[1]))

	cursor.close()
	cnx.close()

	return lines


def fetch_arcs():
	cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
	cursor = cnx.cursor()

	arcs = []
	query = """
		SELECT a, b, c, d
		FROM arc
	"""
	cursor.execute(query)
	for arc in cursor:
		arcs.append((arc[0], arc[1], arc[2], arc[3]))

	cursor.close()
	cnx.close()

	return arcs
