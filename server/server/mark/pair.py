import numpy as np
import mysql.connector
from .edge import get_edges_by_side_id
from itertools import combinations


def get_pairs(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM pair WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    pairs = cursor.fetchall()
    cursor.close()
    cnx.close()
    return pairs


def point_to_line_distance(edges_on_the_same_line, point):
    """
    Calculate the distance between a point and a line

    Parameters
    ----------
    edges_on_the_same_line : list
        list of two edges on the same line
    point : list
        list of the point

    Returns
    -------
    float
        distance between the point and the line
    """
    line_point1, line_point2 = edges_on_the_same_line
    A = np.array(line_point1)
    B = np.array(line_point2)
    P = np.array(point)

    # Calculate the vector AP and vector AB
    AP = P - A
    AB = B - A

    # Calculate the cross product (AP x AB)
    cross_product = np.cross(AP, AB)

    # Calculate the distance
    distance = np.linalg.norm(cross_product) / np.linalg.norm(AB)

    return distance


def unique_tuples(list_of_tuples):
    unique_tuples = []
    seen = set()
    for tuple in list_of_tuples:
        if tuple not in seen:
            unique_tuples.append(tuple)
            seen.add(tuple)
    return unique_tuples


def to_line_edge_list(edge_results1, edge_results2):
    line_edge_list = []
    edges1 = unique_tuples(edge_results1)
    edges2 = unique_tuples(edge_results2)
    if not edges1 or not edges2:
        return []
    edge1_count = len(edges1)
    edge2_count = len(edges2)
    if edge1_count == 1 and edge2_count == 1:
        return []
    if edge1_count > 1:
        # add two of edges1 and one of edges2
        # combinations of edges1
        for i, j in combinations(range(edge1_count), 2):
            for edge2 in edges2:
                line_edge_list.append([[edges1[i], edges1[j]], edge2])

    if edge2_count > 1:
        # add two of edges2 and one of edges1
        # combinations of edges2
        for i, j in combinations(range(edge2_count), 2):
            for edge1 in edges1:
                line_edge_list.append([[edges2[i], edges2[j]], edge1])

    return line_edge_list


def add_line_length(model_id: int, mysql_config: dict, process_id: int):
    pairs = get_pairs(model_id, mysql_config)
    for (pair_id,) in pairs:
        sides = get_sides_by_pair_id(pair_id, mysql_config)
        side1 = sides[0]
        side2 = sides[1]
        length = point_to_line_distance([side1[0:3], side1[3:6]], side2[0:3])
        edge_results1 = get_edges_by_side_id(side1[6], mysql_config, process_id)
        edge_results2 = get_edges_by_side_id(side2[6], mysql_config, process_id)
        line_edge_list = to_line_edge_list(edge_results1, edge_results2)
        if not line_edge_list:
            continue
        distances = []
        for [edges, edge] in line_edge_list:
            # check if edge is not None
            if edge and edge[0] and edge[1]:
                distances.append(point_to_line_distance(edges, edge))
        if len(distances) == 0:
            continue
        measured_length = np.mean(distances)
        measured_length = float(np.round(measured_length, 3))
        add_measured_length(pair_id, length, measured_length, mysql_config, process_id)


def get_sides_by_pair_id(pair_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT x0, y0, z0, x1, y1, z1, id FROM side WHERE pair_id = %s"
    cursor.execute(query, (pair_id,))
    sides = cursor.fetchall()
    cursor.close()
    cnx.close()
    return sides


def add_measured_length(
    pair_id: int,
    length: float,
    measured_length: float,
    mysql_config: dict,
    process_id: int,
):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "UPDATE pair SET length = %s WHERE id = %s"
    cursor.execute(query, (length, pair_id))
    cnx.commit()

    query = "INSERT INTO pair_result (pair_id, process_id, length) VALUES (%s, %s, %s)"
    cursor.execute(query, (pair_id, process_id, measured_length))
    cnx.commit()

    cursor.close()
    cnx.close()


def delete_measured_length(
    mysql_config: dict,
    process_id: int,
):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM pair_result WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    cnx.commit()
    cursor.close()
    cnx.close()


def delete_row_with_model_id(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM pair WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
