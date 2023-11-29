import numpy as np
from server.mark.line import get_sides
import mysql.connector


def sort_sides(sides):
    """
    Sort sides by x, y, z
    """
    sorted_sides = []
    for side in sides:
        side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = side
        if x0 < x1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 < y1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 == y1 and z0 < z1:
            sorted_sides.append(side)
        else:
            sorted_sides.append([side_id, model_id, x1, y1, z1, x0, y0, z0, pair_id])
    return sorted_sides


def import_steps(mysql_config: dict, model_id: int):
    sides = get_sides(mysql_config, model_id)
    sorted_sides = sort_sides(sides)

    np_sides = np.array(sorted_sides)
    xy_points = np_sides[:, [2, 3, 5, 6]]
    _unique, _counts = np.unique(xy_points, axis=0, return_counts=True)
    duplicate_xy_points = _unique[_counts > 1]
    # get rows with duplicate xy points from np_sides
    duplicate_xy_points = duplicate_xy_points.tolist()
    duplicate_rows = []
    for duplicate_xy_point in duplicate_xy_points:
        duplicate_rows.append(
            np.argwhere(
                (np_sides[:, [2, 3, 5, 6]] == duplicate_xy_point).all(axis=1)
            ).flatten()
        )

    steps = []
    for idx in duplicate_rows:
        duplicate_sides = np_sides[idx]
        first_side = duplicate_sides[0]
        second_side = duplicate_sides[1]
        # same line, no step
        if first_side[4] == second_side[4]:
            continue
        if first_side[4] != first_side[7]:
            continue
        if second_side[4] != second_side[7]:
            continue
        steps.append(duplicate_sides)

    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "INSERT INTO trace (model_id, type, start, end, result) VALUES (%s, %s, %s, %s, %s)"
    import_data = []
    for step in steps:
        step = step.tolist()
        model_id = step[0][1]
        trace_type = "step"
        start = step[0][0]
        end = step[1][0]
        height = abs(step[0][4] - step[1][4])
        import_data.append((model_id, trace_type, start, end, height))

    cursor.executemany(query, import_data)
    cnx.commit()
    cursor.close()
