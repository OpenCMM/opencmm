from server.config import MYSQL_CONFIG
from server.listener.mqtt import MqttListener
from server.listener.status import (
    start_measuring,
    update_process_status,
    add_end_timestamp,
)


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
