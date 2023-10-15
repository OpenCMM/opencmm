from cncmark.config import MYSQL_CONFIG
import mysql.connector
from mysql.connector.errors import IntegrityError


def get_center_of_side(side: tuple):
    side_id, x0, y0, z0, x1, y1, z1, pair_id = side
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
    z = (z0 + z1) / 2
    return (x, y, z)


def to_edge_list(sides: list):
    edge_list = []
    for side in sides:
        edge_list.append([side[0]] + list(get_center_of_side(side)))

    return edge_list


def import_edges(sides: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    edges = to_edge_list(sides)
    insert_query = "INSERT INTO edge (side_id, x, y, z)" " VALUES (%s, %s, %s, %s)"
    try:
        cursor.executemany(insert_query, edges)
    except IntegrityError:
        print("Error: unable to import lines")
    cnx.commit()
    cursor.close()
    cnx.close()
