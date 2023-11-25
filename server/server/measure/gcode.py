from datetime import datetime, timedelta
import csv


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
    assert line >= 3
    line -= 3
    row = gcode[line]
    (x, y, first_feedrate) = row_to_xyz_feedrate(row)
    feedrate = first_feedrate / 60  # mm/s
    if line == 0:
        return ((0.0, 0.0), (x, y), feedrate)
    prev_row = gcode[line - 1]
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


def is_point_on_line(p: tuple, p1: tuple, p2: tuple):
    if are_points_equal(p1, p2):
        # The points are the same, so the line has zero length.
        return are_points_equal(p1, p)

    # Check if the slope of the line formed by p1 and p2 is the same as the slope
    # of the line formed by p1 and p.
    slope1 = (p2[1] - p1[1]) / (p2[0] - p1[0]) if (p2[0] - p1[0]) != 0 else float("inf")
    slope2 = (p[1] - p1[1]) / (p[0] - p1[0]) if (p[0] - p1[0]) != 0 else float("inf")

    return (
        round(slope1, 3) == round(slope2, 3)
        and min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0])
        and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])
    )


def get_true_line_number(xy: tuple, line: int, gcode: list) -> int:
    """
    Use xy coordinates as a ground truth to find the line number
    Check if the xy coordinates are within the line
    """
    (start, end, _feedrate) = get_start_end_points_from_line_number(gcode, line)
    if is_point_on_line(xy, start, end):
        return line

    # check the previous line
    (start, end, _feedrate) = get_start_end_points_from_line_number(gcode, line - 1)
    if is_point_on_line(xy, start, end):
        return line - 1

    (start, end, _feedrate) = get_start_end_points_from_line_number(gcode, line - 2)
    if is_point_on_line(xy, start, end):
        return line - 2

    return None
