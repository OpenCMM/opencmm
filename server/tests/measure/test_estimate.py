from server.measure.gcode import load_gcode, row_to_xyz_feedrate
from server.listener.mt import reader
from server.measure.estimate import update_data_after_measurement
from server.config import GCODE_PATH, MYSQL_CONFIG
import mysql.connector
import random
from server.model import add_new_3dmodel
from server.listener import status
from datetime import datetime, timedelta
from server.prepare import get_gcode_filename

z = 10.0


def import_sensor_data(mysql_config: dict, _sensor_data_list: list):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    query = "INSERT INTO sensor(process_id, timestamp, distance) " "VALUES (%s, %s, %s)"
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


def prepare_mock_data(filename: str):
    model_id = add_new_3dmodel(filename)
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    return model_id, process_id


def create_mock_data(filename: str, process_id: int):
    start_coord = (0.0, 0.0)
    mtconnect_mock_data = []
    sensor_mock_data = []
    sample_interval = 0.5
    gcode_filename = get_gcode_filename(filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode = load_gcode(gcode_file_path)
    line = 3
    timestamp = datetime.now()
    for i in range(len(gcode)):
        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = ((x - start_coord[0]) ** 2 + (y - start_coord[1]) ** 2) ** 0.5
        feedrate = round(feedrate_per_min / 60.0, 3)

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
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


def create_mock_missing_data(filename: str, process_id: int):
    start_coord = (0.0, 0.0)
    mtconnect_mock_data = []
    sensor_mock_data = []
    sample_interval = 0.5
    gcode_filename = get_gcode_filename(filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode = load_gcode(gcode_file_path)
    line = 3
    timestamp = datetime.now()
    for i in range(len(gcode)):
        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = ((x - start_coord[0]) ** 2 + (y - start_coord[1]) ** 2) ** 0.5
        feedrate = round(feedrate_per_min / 60.0, 3)

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
            # between 0.9 ~ 1.1
            random_number = random.random() * 0.2 + 0.9
            _x = (
                start_coord[0]
                + (x - start_coord[0])
                * j
                * feedrate
                * sample_interval
                / distance
                * random_number
            )
            _y = (
                start_coord[1]
                + (y - start_coord[1])
                * j
                * feedrate
                * sample_interval
                / distance
                * random_number
            )
            _x = round(_x, 3)
            _y = round(_y, 3)

            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)
            mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)
        last_timestamp = timestamp
        if random_number > 1:
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
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_missing_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc_missing_data():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"
