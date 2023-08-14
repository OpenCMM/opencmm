import numpy as np
from scipy.optimize import least_squares

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
    return (x - cx)**2 + (y - cy)**2 - r**2

def fit_circle(points):
    x = points[:, 0]
    y = points[:, 1]

    initial_params = np.mean(x), np.mean(y), np.std(np.sqrt((x - np.mean(x))**2 + (y - np.mean(y))**2))

    result = least_squares(circle_residuals, initial_params, args=(x, y))
    cx, cy, r = result.x

    return cx, cy, r
