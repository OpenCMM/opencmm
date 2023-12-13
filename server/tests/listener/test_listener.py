from server.listener import listener_start
from server.config import (
    MYSQL_CONFIG,
)
from server.listener import status
from time import sleep
import threading
from .mockmtctagent import start_mock_mtct_agent
import shutil
from .mocksensor import start_mock_sensor
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


def test_listener_start():
    # copy step.STL and create a new file named step2.STL
    source_file = "tests/fixtures/stl/step.STL"
    destination_file = "tests/fixtures/stl/step-integration-tests.STL"

    shutil.copyfile(source_file, destination_file)

    # upload step2.STL
    with open(destination_file, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        model_id = response.json()["model_id"]

    job_info = {
        "three_d_model_id": model_id,
        "measurement_range": 2.0,
        "measure_feedrate": 100.0,
        "move_feedrate": 1000.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    mqtt_log_path = "tests/fixtures/mqtt/process6.json"

    mtct_mock_agent_th = threading.Thread(
        target=start_mock_mtct_agent,
        args=((mqtt_log_path,)),
    )

    sensor_csv_path = "tests/fixtures/csv/sensor.csv"
    sensor_mock = threading.Thread(
        target=start_mock_sensor,
        args=(sensor_csv_path,),
    )

    mtct_mock_agent_th.start()
    sensor_mock.start()
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    listener_start(
        MYSQL_CONFIG,
        process_id,
    )

    sleep(10)

    mtct_mock_agent_th.join()
    sensor_mock.join()
