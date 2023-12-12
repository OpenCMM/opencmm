from server.config import MYSQL_CONFIG
from server.listener.mqtt import MqttListener
from server.listener.status import (
    start_measuring,
    update_process_status,
    add_end_timestamp,
)
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)


def test_import_mtconnect_data_from_mqtt_log():
    model_id = 4
    for i in range(3, 7):
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
