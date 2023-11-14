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
    (x, y, feedrate) = row_to_xyz_feedrate(row)
    if line == 0:
        return ((0.0, 0.0), (x, y))
    prev_row = gcode[line - 1]
    (_x, _y, _feedrate) = row_to_xyz_feedrate(prev_row)
    return ((_x, _y), (x, y))


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
