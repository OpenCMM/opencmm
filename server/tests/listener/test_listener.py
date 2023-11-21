from server.listener import listener_start
from server.config import (
    MQTT_PASSWORD,
    MQTT_USERNAME,
    MYSQL_CONFIG,
    PROCESS_CONTROL_TOPIC,
)
import paho.mqtt.publish as publish
from time import sleep


def test_listener_start():
    listener_start(
        MYSQL_CONFIG,
        1000,
        1,
        (100, 1000),
    )

    sleep(2)
    publish.single(
        PROCESS_CONTROL_TOPIC,
        "stop",
        hostname="localhost",
        auth={"username": MQTT_USERNAME, "password": MQTT_PASSWORD},
    )
