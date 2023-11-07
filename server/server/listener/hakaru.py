import json
import paho.mqtt.client as mqtt
from time import sleep
from server.config import (
    MQTT_BROKER_URL,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    PING_TOPIC,
)

sensor_online = False


def send_config(interval: int, threshold: int):
    """
    Starts the streaming process
    """

    return json.dumps(
        {"command": "config", "interval": interval, "threshold": threshold}
    )


def deep_sleep():
    return json.dumps({"command": "deepSleep"})


def ping_sensor() -> bool:
    """
    Pings the sensor
    """
    global sensor_online
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        client.subscribe(PING_TOPIC)
        client.publish(PING_TOPIC, "ping")

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        global sensor_online
        msg_payload = msg.payload.decode("utf-8")
        if msg.topic == PING_TOPIC:
            if msg_payload == "pong":
                sensor_online = True

    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, 1883, 60)
    client.loop_start()
    sleep(0.5)
    client.unsubscribe(PING_TOPIC)
    client.disconnect()
    client.loop_stop()
    result = sensor_online
    sensor_online = False
    return result
