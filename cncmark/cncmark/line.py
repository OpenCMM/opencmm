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


def import_pair(pair_type: str) -> int:
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    insert_query = "INSERT INTO pair (type) VALUES (%s)"
    cursor.execute(insert_query, (pair_type,))
    cnx.commit()
    cursor.close()
    cnx.close()
    return cursor.lastrowid


def import_sides(pairs: np.ndarray, pair_type: str):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    for pair in pairs:
        pair_id = import_pair(pair_type)
        side_list = to_side_list(pair, pair_id)
        insert_query = (
            "INSERT INTO side (x0, y0, z0, x1, y1, z1, pair_id)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        try:
            cursor.executemany(insert_query, side_list)
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


def import_parallel_lines(lines: np.ndarray):
    x, y, other = get_parallel_lines(lines)
    pairs = get_pairs(x, 0)
    import_sides(pairs, "line")
    pairs = get_pairs(y, 1)
    import_sides(pairs, "line")


def import_edges(edge_list: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    insert_query = "INSERT INTO edge (side_id, x, y, z) VALUES (%s, %s, %s, %s)"
    try:
        cursor.executemany(insert_query, edge_list)
    except IntegrityError:
        print("Error: unable to import edges")
    cnx.commit()
    cursor.close()
    cnx.close()


def import_edges_from_sides(sides: list, number_of_edges_per_side: int = 2):
    edge_list = to_edge_list(sides, number_of_edges_per_side)
    import_edges(edge_list)


def to_edge_list(sides: list, number_of_edges_per_side: int):
    edge_list = []
    for side in sides:
        edge_list += get_edges_for_side(side, number_of_edges_per_side)

    return order_by_xy(edge_list)


def order_by_xy(edge_list):
    # Sort the list based on x and y values
    return sorted(edge_list, key=lambda point: (point[1], point[2]))


def get_edges_for_side(side: tuple, number_of_edges_per_side: int) -> list:
    """
    Returns a list of edges for a side
    Edges need to be distributed evenly along the side
    """
    assert (
        number_of_edges_per_side > 1
    ), "number_of_edges_per_side must be greater than 1"
    side_id, x0, y0, z0, x1, y1, z1, pair_id = side

    edges = []
    for i in range(1, number_of_edges_per_side + 1):
        x = x0 + (x1 - x0) * i / (number_of_edges_per_side + 1)
        y = y0 + (y1 - y0) * i / (number_of_edges_per_side + 1)
        z = z0 + (z1 - z0) * i / (number_of_edges_per_side + 1)
        # x, y, z need to be rounded to 3 decimal places
        x, y, z = round(x, 3), round(y, 3), round(z, 3)
        edges.append((side_id, x, y, z))

    return edges


def get_side(side_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM side WHERE id = %s"
    cursor.execute(query, (side_id,))
    side = cursor.fetchone()
    cursor.close()
    cnx.close()
    return side
