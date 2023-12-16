import math
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


def point_to_line_distance(edges_on_the_same_line: list, point: tuple):
    [line_point1, line_point2] = edges_on_the_same_line
    x1, y1, z1 = line_point1
    x2, y2, z2 = line_point2
    x, y, z = point

    # Calculate the direction vector of the line
    line_direction = (x2 - x1, y2 - y1, z2 - z1)

    # Calculate the vector from line_point1 to the point
    to_point_vector = (x - x1, y - y1, z - z1)

    # Calculate the dot product of the to_point_vector and the line_direction
    dot_product = sum(a * b for a, b in zip(to_point_vector, line_direction))

    # Calculate the magnitude of the line_direction vector squared
    line_length_squared = sum(a * a for a in line_direction)

    # Calculate the parameter t, which is the distance
    # along the line to the closest point
    t = dot_product / line_length_squared

    if t < 0:
        # Closest point is the first line endpoint
        closest_point = line_point1
    elif t > 1:
        # Closest point is the second line endpoint
        closest_point = line_point2
    else:
        # Closest point is along the line
        closest_point = (x1 + t * (x2 - x1), y1 + t * (y2 - y1), z1 + t * (z2 - z1))

    # Calculate the distance between the point and the closest point on the line
    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(point, closest_point)))

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
        total_measured_length = 0
        edge_results1 = get_edges_by_side_id(side1[6], mysql_config, process_id)
        edge_results2 = get_edges_by_side_id(side2[6], mysql_config, process_id)
        sample_size = 0
        line_edge_list = to_line_edge_list(edge_results1, edge_results2)
        if not line_edge_list:
            continue
        for [edges, edge] in line_edge_list:
            # check if edge is not None
            if edge and edge[0] and edge[1]:
                sample_size += 1
                total_measured_length += point_to_line_distance(edges, edge)
        if sample_size == 0:
            continue
        measured_length = round(total_measured_length / sample_size, 3)
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
