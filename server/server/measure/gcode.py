from datetime import datetime, timedelta
import csv
import numpy as np


class LineNumberTooSmall(Exception):
    pass


def load_gcode(filepath: str):
    with open(filepath, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=" ")
        gcode = list(reader)
    gcode = gcode[3:-2]
    return gcode


def row_to_xyz_feedrate(row):
    x = float(row[1][1:])
    y = float(row[2][1:])
    feedrate = float(row[3][1:])
    return (x, y, feedrate)


def get_start_end_points_from_line_number(gcode: list, line: int):
    if line < 3:
        raise LineNumberTooSmall(f"Line number {line} is too small")
    line -= 3
    if line >= len(gcode):
        raise LineNumberTooSmall(f"Line number {line} is too big")
    row = gcode[line]
    if row[0] == "G4":
        # start point is the same as the end point of the previous line
        (x, y, first_feedrate) = row_to_xyz_feedrate(gcode[line - 1])
        return ((x, y), (x, y), 0.0)

    (x, y, first_feedrate) = row_to_xyz_feedrate(row)
    feedrate = first_feedrate / 60  # mm/s
    if line == 0:
        return ((0.0, 0.0), (x, y), feedrate)
    prev_row = gcode[line - 1]
    if prev_row[0] == "G4":
        prev_row = gcode[line - 2]
    (_x, _y, _feedrate) = row_to_xyz_feedrate(prev_row)
    return ((_x, _y), (x, y), feedrate)


def get_timestamp_at_point(
    xy: tuple, point: tuple, feedrate: float, timestamp: datetime, is_start: bool
):
    (x, y) = xy
    (_x, _y) = point
    distance = ((x - _x) ** 2 + (y - _y) ** 2) ** 0.5
    time_diff = distance / feedrate
    if is_start:
        return timestamp - timedelta(seconds=time_diff)
    return timestamp + timedelta(seconds=time_diff)


def are_points_equal(p1: tuple, p2: tuple):
    return round(p1[0], 3) == round(p2[0], 3) and round(p1[1], 3) == round(p2[1], 3)


def closest_distance_between_point_and_line(point, line_start, line_end):
    # Convert input to numpy arrays for vector operations
    point = np.array(point)
    line_start = np.array(line_start)
    line_end = np.array(line_end)

    # Vector representing the direction of the line
    line_direction = line_end - line_start

    # Vector from line start to the given point
    point_to_line_start = point - line_start

    # Calculate the cross product and its magnitude
    cross_product_magnitude = np.linalg.norm(
        np.cross(line_direction, point_to_line_start)
    )

    # Calculate the magnitude of the line direction vector
    line_direction_magnitude = np.linalg.norm(line_direction)

    # Calculate the closest distance
    distance = cross_product_magnitude / line_direction_magnitude

    return distance


def is_point_on_line(p: tuple, p1: tuple, p2: tuple, threshold: float = 0.01):
    if are_points_equal(p1, p2):
        # The points are the same, so the line has zero length.
        return are_points_equal(p1, p)

    distance = closest_distance_between_point_and_line(p, p1, p2)
    is_close = distance < threshold

    return (
        is_close
        and min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0])
        and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])
    )


def get_true_line_number(
    xy: tuple, line: int, gcode: list, first_line_for_tracing: int = None
) -> int:
    """
    Use xy coordinates as a ground truth to find the line number
    Check if the xy coordinates are within the line
    If true line number cannot be found, return None
    """
    if line == 1:
        # the very last line sometimes turns 1 before it supposed to
        last_line = len(gcode) + 2
        (start, end, _feedrate) = get_start_end_points_from_line_number(
            gcode, last_line
        )
        if is_point_on_line(xy, start, end):
            return last_line
        return None

    if first_line_for_tracing:
        assert gcode[first_line_for_tracing - 5][0] == "G4", "G4 is missing"

    try:
        for i in range(3):
            (start, end, _feedrate) = get_start_end_points_from_line_number(
                gcode, line - i
            )
            if is_point_on_line(xy, start, end):
                return line - i
    except LineNumberTooSmall:
        return None

    return None


def get_true_line_and_feedrate(
    xy: tuple, line: int, gcode: list, first_line_for_tracing: int = None
) -> int:
    """
    Use xy coordinates as a ground truth to find the line number
    Check if the xy coordinates are within the line
    """
    lines = []
    if line == 1:
        last_line = len(gcode) + 2
        for i in range(3):
            # the very last line sometimes turns 1 before it supposed to
            (start, end, feedrate) = get_start_end_points_from_line_number(
                gcode, last_line - i
            )
            if i == 0 and are_points_equal(xy, end):
                # already at the end of the line and cannot estimate when it arrived
                if not first_line_for_tracing:
                    # in edge detection mode, this is crucial
                    return lines
                # in tracing mode, the timestamp at the end of the line is not important
            if is_point_on_line(xy, start, end):
                lines.append([last_line - i, feedrate, start, end])
        return lines

    if first_line_for_tracing:
        assert gcode[first_line_for_tracing - 5][0] == "G4", "G4 is missing"

    try:
        for i in range(3):
            (start, end, feedrate) = get_start_end_points_from_line_number(
                gcode, line - i
            )
            if is_point_on_line(xy, start, end):
                lines.append([line - i, feedrate, start, end])
    except LineNumberTooSmall:
        return lines

    return lines


def get_gcode_line_path(gcode_filepath: str):
    gcode_rows = load_gcode(gcode_filepath)
    gcode_line_path = []
    line_number = 3
    prev_xy = [0, 0]
    for row in gcode_rows:
        if row[0] != "G4":
            (x, y, feedrate) = row_to_xyz_feedrate(row)
            gcode_line_path.append([line_number, *prev_xy, x, y, feedrate])
            prev_xy = [x, y]
        line_number += 1

    return gcode_line_path
