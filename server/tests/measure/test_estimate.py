# from server.measure.estimate import update_data_after_measurement
from server.listener.mt import reader
from server.config import MYSQL_CONFIG
import csv
from datetime import datetime, timedelta

process_id = 3
z = 10.0


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


def create_mock_data():
    start_coord = (0.0, 0.0)
    mtconnect_mock_data = []
    sample_interval = 0.5
    gcode = load_gcode("tests/fixtures/gcode/first.STL.gcode")
    line = 3
    timestamp = datetime.now()
    for i in range(len(gcode)):
        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = ((x - start_coord[0]) ** 2 + (y - start_coord[1]) ** 2) ** 0.5
        feedrate = round(feedrate_per_min / 60.0, 3)
        for j in range(int(distance / (feedrate * sample_interval))):
            _x = (
                start_coord[0]
                + (x - start_coord[0]) * j * feedrate * sample_interval / distance
            )
            _y = (
                start_coord[1]
                + (y - start_coord[1]) * j * feedrate * sample_interval / distance
            )
            _x = round(_x, 3)
            _y = round(_y, 3)

            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)
            mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)

        line += 1
        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)


def test_update_data_after_measurement():
    create_mock_data()
    # update_data_after_measurement()
