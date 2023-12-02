import numpy as np
from server.mark.line import get_sides
from .trace import import_traces


def import_slopes(mysql_config: dict, model_id: int, lines: list):
    sides = get_sides(mysql_config, model_id)
    np_sides = np.array(sides)
    traces = []

    for lines_on_facet in lines:
        slope_pair = None
        for i, pair in enumerate(lines_on_facet):
            # check only first line
            first_line = pair[0]
            # check if z values are the same
            if first_line[0][2] != first_line[1][2]:
                if i == 0:
                    slope_pair = lines_on_facet[1]
                else:
                    slope_pair = lines_on_facet[0]

        if slope_pair is None:
            continue

        # low to high
        if slope_pair[0][0][2] < slope_pair[1][0][2]:
            slope_start = slope_pair[0]
            slope_end = slope_pair[1]
        else:
            slope_start = slope_pair[1]
            slope_end = slope_pair[0]

        slope_start_middle_point = (slope_start[0] + slope_start[1]) / 2
        slope_end_middle_point = (slope_end[0] + slope_end[1]) / 2

        slope_start_data = slope_start.flatten()
        slope_end_data = slope_end.flatten()
        for side in np_sides:
            if (side[2:8] == slope_start_data).all():
                start_side_id = side[0]
            if (side[2:8] == slope_end_data).all():
                end_side_id = side[0]

        angle = get_angle(slope_start_middle_point, slope_end_middle_point)
        traces.append([model_id, "slope", start_side_id, end_side_id, angle])

    if traces:
        import_traces(mysql_config, traces)


def get_angle(start_point: np.ndarray, end_point: np.ndarray):
    # Calculate the vector representing the line
    line_vector = end_point - start_point
    # Calculate the angle between the line vector and the xy plane
    xy_plane_vector = np.array([1.0, 0.0, 0.0])
    angle = np.arccos(
        np.dot(line_vector, xy_plane_vector)
        / (np.linalg.norm(line_vector) * np.linalg.norm(xy_plane_vector))
    )

    # Convert the angle to degrees
    angle_degrees = np.rad2deg(angle)
    # between 0 and 90
    if angle_degrees > 90:
        angle_degrees = 180 - angle_degrees
    return angle_degrees
