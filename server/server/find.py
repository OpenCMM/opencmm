import mysql.connector
from mysql.connector.errors import IntegrityError


def find_edges(process_id: int, mysql_config: dict):
    edges = get_sensor_data(process_id, mysql_config)
    if len(edges) > 0:
        # remove the starting point
        edges.pop(0)
    return edges


def get_sensor_data(process_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM sensor WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows


def check_if_edge_is_found(
    distance: str, prev_distance: str or float, minimal_diff: float = 5.0
):
    if distance == "" and prev_distance == "":
        return False
    if distance == "" or prev_distance == "":
        return True
    if abs(float(distance) - float(prev_distance)) > minimal_diff:
        return True
    return False


def get_edge_data(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id,x,y,z FROM edge WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def identify_close_edge(edges, measured_edges, offset: tuple, distance_threshold=2.5):
    update_list = []
    for id, x, y, z in edges:
        # add offset
        (x, y, z) = (x + offset[0], y + offset[1], z + offset[2])
        min_distance = 999999.0
        data_with_min_distance = []
        for measured_edge in measured_edges:
            rx = measured_edge[1]
            ry = measured_edge[2]
            distance = ((x - rx) ** 2 + (y - ry) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                data_with_min_distance = (rx, ry, z, id)

        if min_distance <= distance_threshold:
            update_list.append(data_with_min_distance)

    return update_list


def add_measured_edge_coord(edge_list: list, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "UPDATE edge SET rx = %s, ry = %s, rz = %s WHERE id = %s"
    try:
        cursor.executemany(query, edge_list)
    except IntegrityError:
        print("Error: unable to import lines")
    cnx.commit()
    cursor.close()
    cnx.close()


def process_edges(
    model_id: int, process_id: int, mysql_config: dict, minimal_diff: float = 5.0
) -> int:
    """
    Identify the edges from the sensor data and add the coordinates to the database
    """
    measured_edges = find_edges(process_id, mysql_config, minimal_diff)
    edge_data = get_edge_data(model_id, mysql_config)
    update_list = identify_close_edge(edge_data, measured_edges)
    add_measured_edge_coord(update_list, mysql_config)
    edge_count = len(edge_data)
    return edge_count
