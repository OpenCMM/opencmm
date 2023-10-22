from cncmark.config import MYSQL_CONFIG
import numpy as np
from scipy.optimize import least_squares
import mysql.connector
from mysql.connector.errors import IntegrityError


def get_edges_for_arc(arc_id: int, arc_points: np.ndarray, number_of_edges: int):
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
        edges.append((arc_id, round(x, 3), round(y, 3), round(z, 3)))

    return edges


def import_arcs(arcs: list):
    for arc_points in arcs:
        arc_info = to_arc_info(arc_points)
        arc_id = import_arc(arc_info)
        edges = get_edges_for_arc(arc_id, arc_points, 3)
        import_edges(edges)


def import_edges(edge_list: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    insert_query = "INSERT INTO edge (arc_id, x, y, z) VALUES (%s, %s, %s, %s)"
    try:
        cursor.executemany(insert_query, edge_list)
    except IntegrityError:
        print("Error: unable to import edges")
    cnx.commit()
    cursor.close()
    cnx.close()


def import_arc(arc_info: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    insert_query = "INSERT INTO arc (radius, cx, cy, cz) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_query, tuple(arc_info))
    cnx.commit()
    cursor.close()
    cnx.close()
    return cursor.lastrowid


def to_arc_info(arc_points: np.ndarray):
    radius, center = get_arc_info(arc_points)
    arc_info = [
        float(radius),
        float(center[0]),
        float(center[1]),
        float(center[2]),
    ]
    return [round(x, 3) for x in arc_info]


def get_arc_info(arc_points: list):
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
