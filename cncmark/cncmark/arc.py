import numpy as np
from cncmark.config import MYSQL_CONFIG
from scipy.optimize import least_squares
import mysql.connector
from mysql.connector.errors import IntegrityError
from cncmark.point import point_id


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


def circle_residuals(params, x, y):
    cx, cy, r = params
    return (x - cx) ** 2 + (y - cy) ** 2 - r**2


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


def import_arcs(arcs: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    arc_list = [to_arc_list(ab) for ab in arcs]

    insert_query = (
        "INSERT INTO arc (a, b, c, d, radius, cx, cy, cz)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )

    try:
        cursor.executemany(insert_query, arc_list)
    except IntegrityError:
        print("Error: unable to import arcs")
    cnx.commit()
    cursor.close()
    cnx.close()


def to_arc_list(arc_points: list):
    """
    Pick 4 points that define the arc
    """
    count = len(arc_points)
    if count < 4:
        raise ValueError("Not enough points to define arc")

    a = arc_points[0]  # first point
    d = arc_points[-1]  # last point

    one_third = count // 3
    b = arc_points[one_third - 1]
    c = arc_points[one_third * 2 - 1]
    radius, center = get_arc_info(arc_points)
    return [
        point_id(a),
        point_id(b),
        point_id(c),
        point_id(d),
        radius,
        center[0],
        center[1],
        center[2],
    ]
