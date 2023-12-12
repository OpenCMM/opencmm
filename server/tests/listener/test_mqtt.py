from server.config import MYSQL_CONFIG
from server.listener.mqtt import MqttListener
from server.listener.status import (
    start_measuring,
    update_process_status,
    add_end_timestamp,
)
from fastapi.testclient import TestClient
from server.main import app
import shutil

client = TestClient(app)


def test_import_mtconnect_data_from_mqtt_log():
    # copy step.STL and create a new file named step2.STL
    source_file = "tests/fixtures/stl/step.STL"
    destination_file = "tests/fixtures/stl/step2.STL"

    shutil.copyfile(source_file, destination_file)

    # upload step2.STL
    with open(destination_file, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        model_id = response.json()["model_id"]

    job_info = {
        "three_d_model_id": model_id,
        "range": 2.5,
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

    for i in range(3, 6):
        process_id = start_measuring(model_id, MYSQL_CONFIG, "running")
        mqtt_listener = MqttListener(MYSQL_CONFIG, process_id)
        mqtt_listener.import_mtconnect_data_from_mqtt_log(
            f"tests/fixtures/mqtt/process{i}.json"
        )
        add_end_timestamp(MYSQL_CONFIG, process_id)
        update_process_status(MYSQL_CONFIG, process_id, "done")

        response = client.get(
            (
                "/result/mtconnect/avg/delay"
                f"?model_id={model_id}&process_id={process_id}"
            )
        )
        assert response.status_code == 200
        result = response.json()
        delay = result["avg"]
        print(f"process{i}", process_id)
        print("delay:", delay)
        assert delay < 0.03

        response = client.get(
            (
                "/result/mtconnect/missing/lines/travel/time/diff"
                f"?model_id={model_id}&process_id={process_id}"
            )
        )
        assert response.status_code == 200
        result = response.json()
        diff = result["avg"]
        print("diff:", diff)
        assert diff < 0.03


def test_import_mtconnect_data_from_mqtt_process6():
    source_file = "tests/fixtures/stl/step.STL"
    destination_file = "tests/fixtures/stl/step3.STL"

    shutil.copyfile(source_file, destination_file)

    # upload step2.STL
    with open(destination_file, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        model_id = response.json()["model_id"]

    job_info = {
        "three_d_model_id": model_id,
        "range": 2.0,
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

    process_id = start_measuring(model_id, MYSQL_CONFIG, "running")
    mqtt_listener = MqttListener(MYSQL_CONFIG, process_id)
    mqtt_listener.import_mtconnect_data_from_mqtt_log(
        "tests/fixtures/mqtt/process6.json"
    )
    add_end_timestamp(MYSQL_CONFIG, process_id)
    update_process_status(MYSQL_CONFIG, process_id, "done")

    response = client.get(
        ("/result/mtconnect/avg/delay" f"?model_id={model_id}&process_id={process_id}")
    )
    assert response.status_code == 200
    result = response.json()
    delay = result["avg"]
    print("process6", process_id)
    print("delay:", delay)
    assert delay < 0.03

    response = client.get(
        (
            "/result/mtconnect/missing/lines/travel/time/diff"
            f"?model_id={model_id}&process_id={process_id}"
        )
    )
    assert response.status_code == 200
    result = response.json()
    diff = result["avg"]
    print("diff:", diff)
    assert diff < 0.03
