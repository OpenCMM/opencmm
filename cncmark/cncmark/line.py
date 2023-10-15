from cncmark.config import MYSQL_CONFIG
import numpy as np
import mysql.connector
from mysql.connector.errors import IntegrityError
from .point import point_id
from itertools import combinations


def import_lines(lines: np.ndarray):
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


def get_parallel_lines(lines: np.ndarray):
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

    return np.array(x_parallel_lines), np.array(y_parallel_lines), np.array(other_lines)


def get_pairs(parallel_lines: np.ndarray, direction: int):
    pairs = []

    # Loop through unique pairs of indices
    for i, j in combinations(range(len(parallel_lines)), 2):
        line0 = parallel_lines[i]
        line1 = parallel_lines[j]

        if (
            line0[0][direction] == line1[0][direction]
            and line0[1][direction] == line1[1][direction]
        ) or (
            line0[0][direction] == line1[1][direction]
            and line0[1][direction] == line1[0][direction]
        ):
            pairs.append([line0, line1])

    return pairs


def to_side_list(pairs: np.ndarray, pair_id: int):
    side_list = []
    for pair in pairs:
        result = pair.flatten().tolist()
        result.append(pair_id)
        side_list.append(result)
    return side_list


def import_sides(pairs: np.ndarray):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    pair_id = 0
    for pair in pairs:
        side_list = to_side_list(pair, pair_id)
        insert_query = (
            "INSERT INTO side (x0, y0, z0, x1, y1, z1, pair_id)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        try:
            cursor.executemany(insert_query, side_list)
            pair_id += 1
        except IntegrityError:
            print("Error: unable to import lines")
        cnx.commit()
    cursor.close()
    cnx.close()


def get_sides():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM side"
    cursor.execute(query)
    sides = cursor.fetchall()
    cursor.close()
    cnx.close()
    return sides
