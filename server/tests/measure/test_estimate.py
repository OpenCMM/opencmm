from server.measure.gcode import load_gcode, row_to_xyz_feedrate
from server.listener.mt import reader
from server.config import MYSQL_CONFIG
import mysql.connector
import random
from datetime import datetime, timedelta

process_id = 1
z = 10.0


def import_sensor_data(mysql_config: dict, _sensor_data_list: list):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    query = (
        "INSERT INTO sensor(process_id, timestamp, distance) "
        "VALUES (%s, %s, %s)"
    )
    mysql_cur.executemany(
        query,
        _sensor_data_list,
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


def get_random_sensor_data():
    sensor_output = random.randint(0, 19000)
    return sensor_output


def get_random_timestamp_between_two_timestamps(first_timestamp, last_timestamp):
    timestamp_diff = last_timestamp - first_timestamp
    random_diff = (timestamp_diff * random.random() / 2).total_seconds()
    timestamp = first_timestamp + timedelta(seconds=random_diff)
    unix_timestamp = timestamp.timestamp()
    rounded_unix_timestamp = round(unix_timestamp, 3)
    return datetime.fromtimestamp(rounded_unix_timestamp)


def create_mock_data():
    start_coord = (0.0, 0.0)
    mtconnect_mock_data = []
    sensor_mock_data = []
    sample_interval = 0.5
    gcode = load_gcode("tests/fixtures/gcode/first.STL.gcode")
    line = 3
    timestamp = datetime.now()
    for i in range(len(gcode)):
        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = ((x - start_coord[0]) ** 2 + (y - start_coord[1]) ** 2) ** 0.5
        feedrate = round(feedrate_per_min / 60.0, 3)

        first_timestamp = timestamp
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
        last_timestamp = timestamp
        if line % 2 == 0:
            sensor_output = get_random_sensor_data()
            sensor_timestamp = get_random_timestamp_between_two_timestamps(
                first_timestamp, last_timestamp
            )
            sensor_mock_data.append((process_id, sensor_timestamp, sensor_output))

        line += 1
        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)
    import_sensor_data(MYSQL_CONFIG, sensor_mock_data)


def test_update_data_after_measurement():
    create_mock_data()
    # update_data_after_measurement(MYSQL_CONFIG, process_id, 1)
