import pytest
from server.listener.hakaru import (
    ping_sensor,
    listen_sensor,
)
from time import sleep
from server.config import MYSQL_CONFIG

MQTT_BROKER_URL = "192.168.10.104"


@pytest.mark.skip(reason="No MQTT broker running")
def test_ping_sensor():
    assert ping_sensor() is True


@pytest.mark.skip(reason="No MQTT broker running")
def test_listen_sensor():
    interval = 100
    threshold = 1000
    streaming_config = (interval, threshold)
    process_id = 1
    listen_sensor(MQTT_BROKER_URL, process_id, MYSQL_CONFIG, streaming_config)
    sleep(20)
