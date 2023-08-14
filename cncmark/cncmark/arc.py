def pick_arc_points(arc_points: list):
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

    return a, b, c, d
