import numpy as np
from scipy.optimize import least_squares
import mysql.connector
from server.config import get_config
from mysql.connector.errors import IntegrityError


def get_edges_for_arc(
    model_id: int, arc_id: int, arc_points: np.ndarray, number_of_edges: int
):
    """
    Returns a list of edges for an arc/circle
    Edges need to be distributed evenly along the arc
    """
    count = len(arc_points)
    if count < 4:
        raise ValueError("Not enough points to define arc")

    if number_of_edges < 3:
        raise ValueError("Not enough edges to define arc")

    interval = count // number_of_edges

    edges = []
    for i in range(number_of_edges):
        x, y, z = arc_points[i * interval].tolist()
        edges.append((model_id, arc_id, round(x, 3), round(y, 3), round(z, 3)))

    return edges


def import_arcs(model_id: int, arcs: list, mysql_config: dict):
    for arc_points in arcs:
        arc_info = to_arc_info(model_id, arc_points)
        arc_id = import_arc(arc_info, mysql_config)
        sample_size = get_config()["edge"]["arc"]["number"]
        edges = get_edges_for_arc(model_id, arc_id, arc_points, sample_size)
        import_edges(edges, mysql_config)


def import_edges(edge_list: list, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    insert_query = (
        "INSERT INTO edge (model_id, arc_id, x, y, z) VALUES (%s, %s, %s, %s, %s)"
    )
    try:
        cursor.executemany(insert_query, edge_list)
    except IntegrityError:
        print("Error: unable to import edges")
    cnx.commit()
    cursor.close()
    cnx.close()


def import_arc(arc_info: list, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    insert_query = (
        "INSERT INTO arc (model_id, radius, cx, cy, cz) VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.execute(insert_query, tuple(arc_info))
    cnx.commit()
    cursor.close()
    cnx.close()
    return cursor.lastrowid


def to_arc_info(model_id: int, arc_points: np.ndarray):
    radius, center = get_arc_info(arc_points)
    arc_info = [
        model_id,
        float(radius),
        float(center[0]),
        float(center[1]),
        float(center[2]),
    ]
    return [round(x, 3) for x in arc_info]


def get_arc_info(arc_points: np.ndarray):
    """
    Get information about arc

    Parameters
    ----------
    arc_points : list
        List of arc coordinates [(x,y,z), (x,y,z)]

    Returns
    -------
    radius : float
        Radius of arc
    center : np.array
        Center of arc
    """
    center_x, center_y, radius = fit_circle(arc_points[:, :2])
    center = np.array([center_x, center_y, arc_points[0, 2]])
    return radius, center


def fit_circle(points):
    x = points[:, 0]
    y = points[:, 1]

    initial_params = (
        np.mean(x),
        np.mean(y),
        np.std(np.sqrt((x - np.mean(x)) ** 2 + (y - np.mean(y)) ** 2)),
    )

    result = least_squares(circle_residuals, initial_params, args=(x, y))
    cx, cy, r = result.x

    return cx, cy, r


def circle_residuals(params, x, y):
    cx, cy, r = params
    return (x - cx) ** 2 + (y - cy) ** 2 - r**2


def get_arc(arc_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM arc WHERE id = %s"
    cursor.execute(query, (arc_id,))
    arc = cursor.fetchone()
    cursor.close()
    cnx.close()
    return arc


def get_arcs(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM arc WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    arcs = cursor.fetchall()
    cursor.close()
    cnx.close()
    return arcs


def get_arc_edge_result(arc_id: int, process_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "SELECT edge_result.x,edge_result.y,edge_result.z FROM edge "
        "INNER JOIN edge_result "
        "ON edge.id = edge_result.edge_id "
        "WHERE arc_id = %s AND process_id = %s"
    )
    cursor.execute(query, (arc_id, process_id))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def add_measured_arc_info(model_id: int, mysql_config: dict, process_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()

    arcs = get_arcs(mysql_config, model_id)
    for arc in arcs:
        arc_id = arc[0]
        edges = get_arc_edge_result(arc_id, process_id, mysql_config)
        if len(edges) < 3:
            # cannot calculate arc with less than 3 edges
            continue
        try:
            radius, center = get_arc_info(np.array(edges))
            query = (
                "INSERT INTO arc_result (radius, cx, cy, cz, arc_id, process_id) "
                "VALUES (%s, %s, %s, %s, %s, %s) "
            )
            data = [radius, center[0], center[1], center[2]]
            data = [round(x, 3) for x in data]
            data.append(arc_id)
            data.append(process_id)
            cursor.execute(query, tuple(data))
            cnx.commit()
        except TypeError:
            continue
    cursor.close()
    cnx.close()


def delete_measured_arc_info(
    mysql_config: dict,
    process_id: int,
):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM arc_result WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    cnx.commit()
    cursor.close()
    cnx.close()


def delete_arcs_with_model_id(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM arc WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
