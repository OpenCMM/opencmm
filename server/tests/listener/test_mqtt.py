from server.config import MYSQL_CONFIG
from server.listener.mqtt import MqttListener
from server.listener.status import (
    start_measuring,
    update_process_status,
    add_end_timestamp,
)


def test_import_mtconnect_data_from_mqtt_log():
    process_id = start_measuring(2, MYSQL_CONFIG, "running")
    mqtt_listener = MqttListener(MYSQL_CONFIG, process_id)
    mqtt_listener.import_mtconnect_data_from_mqtt_log(
        "tests/fixtures/mqtt/process6.json"
    )
    add_end_timestamp(MYSQL_CONFIG, process_id)
    update_process_status(MYSQL_CONFIG, process_id, "done")
