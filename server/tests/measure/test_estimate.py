from server.measure.gcode import load_gcode, row_to_xyz_feedrate
from server.listener.mt import reader
from server.measure.estimate import update_data_after_measurement
from server.config import GCODE_PATH, MODEL_PATH, MYSQL_CONFIG, get_config
import mysql.connector
import random
from server.model import add_new_3dmodel
from server.listener import status
from datetime import datetime, timedelta
from server.mark.gcode import get_gcode_filename
from fastapi.testclient import TestClient
from server.main import app
from .sensor import MockSensor

client = TestClient(app)
z = 10.0

conf = get_config()
mtconnect_latency = conf["mtconnect"]["latency"]
beam_diameter = conf["sensor"]["beam_diameter"]


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


def create_sensor_data_row(_first_timestamp, _last_timestamp, _process_id):
    sensor_output = get_random_sensor_data()
    sensor_timestamp = get_random_timestamp_between_two_timestamps(
        _first_timestamp, _last_timestamp
    )
    return (_process_id, sensor_timestamp, sensor_output)


def get_xy_for_mtconnect(start_coord, feedrate, sample_interval, direction):
    (x, y) = start_coord
    _x = x + direction[0] * feedrate * sample_interval
    _y = y + direction[1] * feedrate * sample_interval
    _x = round(_x, 3)
    _y = round(_y, 3)
    return _x, _y


def get_distance_between_two_points(start_coord, end_coord):
    return (
        (end_coord[0] - start_coord[0]) ** 2 + (end_coord[1] - start_coord[1]) ** 2
    ) ** 0.5


def get_direction(start_coord, end_coord):
    distance = get_distance_between_two_points(start_coord, end_coord)
    direction = (end_coord[0] - start_coord[0], end_coord[1] - start_coord[1])
    # direction to unit vector
    direction = tuple([round(x / distance, 3) for x in direction])
    return direction


def create_mock_perfect_data(filename: str, process_id: int):
    conf = get_config()
    sensor_response_time = conf["sensor"]["response_time"]  # in ms
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
        init_coord = start_coord
        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = get_distance_between_two_points(start_coord, (x, y))
        feedrate = feedrate_per_min / 60.0
        direction = get_direction(start_coord, (x, y))
        timestamp += timedelta(seconds=sample_interval)
        for j in range(int(distance / (feedrate * sample_interval))):
            timestamp += timedelta(seconds=sample_interval)
            timestamp_with_latency = timestamp + timedelta(
                milliseconds=mtconnect_latency
            )
            _x, _y = get_xy_for_mtconnect(
                start_coord, feedrate, sample_interval, direction
            )
            _current_row = (
                process_id,
                timestamp_with_latency,
                _x,
                _y,
                z,
                line,
                feedrate,
            )
            if j != 0:
                mtconnect_mock_data.append(_current_row)
            start_coord = (_x, _y)
        if line % 2 == 0:
            sensor_output = get_random_sensor_data()
            target_coord = ((x + init_coord[0]) / 2, (y + init_coord[1]) / 2)
            distance_to_target = get_distance_between_two_points(
                start_coord, target_coord
            )
            distance_to_target += beam_diameter / 1000
            time_to_substract = distance_to_target / feedrate
            sensor_timestamp = (
                timestamp
                - timedelta(seconds=time_to_substract)
                + timedelta(milliseconds=sensor_response_time)
            )
            unix_timestamp = sensor_timestamp.timestamp()
            rounded_unix_timestamp = round(unix_timestamp, 3)
            sensor_timestamp = datetime.fromtimestamp(rounded_unix_timestamp)
            sensor_mock_data.append((process_id, sensor_timestamp, sensor_output))

        line += 1
        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)
    import_sensor_data(MYSQL_CONFIG, sensor_mock_data)


def create_mock_data(filename: str, process_id: int):
    start_coord = (0.0, 0.0)
    mtconnect_mock_data = []
    sensor_mock_data = []
    sample_interval = 0.5
    gcode_filename = get_gcode_filename(filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode = load_gcode(gcode_file_path)
    mock_sensor = MockSensor(f"{MODEL_PATH}/{filename}")
    is_tracing = False
    timestamp = datetime.now()
    for i in range(len(gcode)):
        line = i + 3
        if gcode[i][0] == "G4":
            # start to measure steps or slopes
            is_tracing = True
            continue

        (x, y, feedrate_per_min) = row_to_xyz_feedrate(gcode[i])
        distance = get_distance_between_two_points(start_coord, (x, y))
        feedrate = round(feedrate_per_min / 60.0, 3)
        direction = get_direction(start_coord, (x, y))

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
            _x, _y = get_xy_for_mtconnect(
                start_coord, feedrate, sample_interval, direction
            )
            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)
            mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)

            if is_tracing and line % 2 == 1:
                _sensor_timestamp = timestamp - timedelta(seconds=sample_interval)
                sensor_output = mock_sensor.get_sensor_output((_x, _y, 100.0))
                sensor_mock_data.append((process_id, _sensor_timestamp, sensor_output))

        last_timestamp = timestamp

        if line % 2 == 0 and not is_tracing:
            sensor_data_row = create_sensor_data_row(
                first_timestamp, last_timestamp, process_id
            )
            sensor_mock_data.append(sensor_data_row)

        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)
    import_sensor_data(MYSQL_CONFIG, sensor_mock_data)


def create_mock_missing_data(filename: str, process_id: int):
    """
    random mtconnect interval
    missing sensor data
    """
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
        distance = get_distance_between_two_points(start_coord, (x, y))
        feedrate = round(feedrate_per_min / 60.0, 3)
        direction = get_direction(start_coord, (x, y))

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
            # between 0.9 ~ 1.1
            random_number = random.random() * 0.2 + 0.9
            _x, _y = get_xy_for_mtconnect(
                start_coord, feedrate, sample_interval * random_number, direction
            )
            _x = round(_x, 3)
            _y = round(_y, 3)

            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)
            mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)
        last_timestamp = timestamp

        sensor_random_number = random.random()
        if sensor_random_number > 0.1:
            sensor_data_row = create_sensor_data_row(
                first_timestamp, last_timestamp, process_id
            )
            sensor_mock_data.append(sensor_data_row)

        line += 1
        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)
    import_sensor_data(MYSQL_CONFIG, sensor_mock_data)


def create_mock_multiple_edges(filename: str, process_id: int):
    """
    random mtconnect interval
    multiple edges per line
    """
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
        distance = get_distance_between_two_points(start_coord, (x, y))
        feedrate = round(feedrate_per_min / 60.0, 3)
        direction = get_direction(start_coord, (x, y))

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
            # between 0.9 ~ 1.1
            random_number = random.random() * 0.2 + 0.9
            _x, _y = get_xy_for_mtconnect(
                start_coord, feedrate, sample_interval * random_number, direction
            )
            _x = round(_x, 3)
            _y = round(_y, 3)

            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)
            mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)
        last_timestamp = timestamp

        sensor_random_number = random.random()
        if sensor_random_number > 0.1:
            sensor_output = get_random_sensor_data()
            sensor_timestamp = get_random_timestamp_between_two_timestamps(
                first_timestamp, last_timestamp
            )
            sensor_mock_data.append((process_id, sensor_timestamp, sensor_output))

            if sensor_random_number > 0.8:
                sensor_output = get_random_sensor_data()
                sensor_timestamp = get_random_timestamp_between_two_timestamps(
                    sensor_timestamp, last_timestamp
                )
                sensor_mock_data.append((process_id, sensor_timestamp, sensor_output))
        line += 1
        start_coord = (x, y)

    reader.import_mtconnect_data(MYSQL_CONFIG, mtconnect_mock_data)
    import_sensor_data(MYSQL_CONFIG, sensor_mock_data)


def create_mock_missing_mtconnect_data(filename: str, process_id: int):
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
        distance = get_distance_between_two_points(start_coord, (x, y))
        feedrate = round(feedrate_per_min / 60.0, 3)
        direction = get_direction(start_coord, (x, y))

        timestamp += timedelta(seconds=sample_interval)
        first_timestamp = timestamp
        for j in range(1, int(distance / (feedrate * sample_interval))):
            # between 0.9 ~ 1.1
            random_number = random.random() * 0.2 + 0.9
            _x, _y = get_xy_for_mtconnect(
                start_coord, feedrate, sample_interval * random_number, direction
            )
            _x = round(_x, 3)
            _y = round(_y, 3)

            _current_row = (process_id, timestamp, _x, _y, z, line, feedrate)

            # intentionally missing data
            if line % 10 != 0:
                mtconnect_mock_data.append(_current_row)
            timestamp += timedelta(seconds=sample_interval)
            start_coord = (_x, _y)
        last_timestamp = timestamp

        sensor_random_number = random.random()
        if sensor_random_number > 0.1:
            sensor_output = get_random_sensor_data()
            sensor_timestamp = get_random_timestamp_between_two_timestamps(
                first_timestamp, last_timestamp
            )
            sensor_mock_data.append((process_id, sensor_timestamp, sensor_output))

            if sensor_random_number > 0.8:
                sensor_output = get_random_sensor_data()
                sensor_timestamp = get_random_timestamp_between_two_timestamps(
                    sensor_timestamp, last_timestamp
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


def test_update_data_after_measurement_multiple_edges():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc_multiple_edges():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_different_gcode_params():
    job_info = {
        "three_d_model_id": 3,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 2000.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_different_gcode_params_with_arc():
    job_info = {
        "three_d_model_id": 4,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 2000.0,
        "x_offset": 50.0,
        "y_offset": -65.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_perfect_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_perfect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/lines?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    lines = response.json()["lines"]
    for [_id, length, estimated_length] in lines:
        assert abs(length - estimated_length) < 0.005

    response = client.get(f"/result/arcs?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    arcs = response.json()["arcs"]
    for arc in arcs:
        radius = arc[1]
        estimated_radius = arc[5]
        assert abs(radius - estimated_radius) < 0.005


def test_update_data_after_measurement_perfect_data_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_perfect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/lines?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    lines = response.json()["lines"]
    for [_id, length, estimated_length] in lines:
        assert abs(length - estimated_length) < 0.005

    response = client.get(f"/result/arcs?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    arcs = response.json()["arcs"]
    for arc in arcs:
        radius = arc[1]
        estimated_radius = arc[5]
        assert abs(radius - estimated_radius) < 0.01


def test_update_data_after_measurement_missing_mtconnect_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_mtconnect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_missing_mtconnect_data_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_mtconnect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_step():
    filename = "step.STL"
    model_id = 5
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/steps?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    steps = response.json()["steps"]
    height = steps[0][1]
    estimated_height = steps[0][2]
    assert height == 3.0
    assert estimated_height == 3.0
