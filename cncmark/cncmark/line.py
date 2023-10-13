from cncmark.config import MYSQL_CONFIG
import numpy as np
import mysql.connector
from mysql.connector.errors import IntegrityError
from .point import point_id


def import_lines(lines: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    line_list = [to_line_list(ab) for ab in lines]

    insert_query = "INSERT INTO line (a, b, length) VALUES (%s, %s, %s)"

    try:
        cursor.executemany(insert_query, line_list)
    except IntegrityError:
        print("Error: unable to import lines")
    cnx.commit()
    cursor.close()
    cnx.close()


def to_line_list(ab: list):
    a = ab[0]
    b = ab[1]
    length = np.linalg.norm(a - b)
    return [point_id(a), point_id(b), float(length)]

def get_parallel_lines(lines: list):
    x_parallel_lines = []
    y_parallel_lines = []
    other_lines = []
    for line in lines:
        # check if line is parallel to x or y axis
        x1, y1, _ = line[0]
        x2, y2, _ = line[1]

        if x1 == x2:
            # line is parallel to y axis
            y_parallel_lines.append(line)
        elif y1 == y2:
            # line is parallel to x axis
            x_parallel_lines.append(line)
        else:
            other_lines.append(line)

    return x_parallel_lines, y_parallel_lines, other_lines
