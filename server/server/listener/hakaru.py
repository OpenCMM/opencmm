import json
import paho.mqtt.client as mqtt
from time import sleep
import mysql.connector
from server.config import (
    CONTROL_SENSOR_TOPIC,
    IMPORT_SENSOR_TOPIC,
    LISTENER_LOG_TOPIC,
    MQTT_BROKER_URL,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    PING_TOPIC,
    PONG_TOPIC,
    PROCESS_CONTROL_TOPIC,
    RECEIVE_DATA_TOPIC,
)
import logging
from server.measure.sensor import mm_to_sensor_output_diff

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

sensor_online = False
sensor_data_list = []


def parse_sensor_data(payload: str):
    """
    Parses sensor data from payload
    """
    data = json.loads(payload)
    sensor_data = data["data"]
    unix_timestamp = data["timestamp"]
    millis = data["millis"]
    # combine timestamp and millis
    timestamp = unix_timestamp + millis / 1000
    return (int(sensor_data), timestamp)


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
        client.subscribe(PONG_TOPIC)
        client.publish(PING_TOPIC, "ping")

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        global sensor_online
        msg_payload = msg.payload.decode("utf-8")
        if msg.topic == PONG_TOPIC:
            if msg_payload == "pong":
                sensor_online = True

    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, 1883, 60)
    client.loop_start()
    sleep(0.5)
    client.unsubscribe(PONG_TOPIC)
    client.disconnect()
    client.loop_stop()
    result = sensor_online
    sensor_online = False
    return result


def import_sensor_data(mysql_config: dict):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    query = (
        "INSERT INTO sensor(process_id, timestamp, distance) "
        "VALUES (%s, FROM_UNIXTIME(%s), %s)"
    )
    mysql_cur.executemany(
        query,
        sensor_data_list,
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


def listen_sensor(
    mqtt_url: str, process_id: int, mysql_config: dict, streaming_config: tuple
):
    global sensor_data_list
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        logger.info("receive_sensor_data(): connected")
        client.subscribe(RECEIVE_DATA_TOPIC)
        client.subscribe(PROCESS_CONTROL_TOPIC)

        # send config to sensor
        (interval, threshold_in_mm) = streaming_config
        threshold = int(mm_to_sensor_output_diff(threshold_in_mm))
        client.publish(CONTROL_SENSOR_TOPIC, send_config(interval, threshold))
        logger.info("sent config to sensor")

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        if msg.topic == RECEIVE_DATA_TOPIC:
            try:
                (sensor_data, timestamp) = parse_sensor_data(
                    msg.payload.decode("utf-8")
                )
                sensor_data_list.append((process_id, timestamp, sensor_data))
            except Exception as e:
                logger.warning(e)
                return

        elif (
            msg.topic == PROCESS_CONTROL_TOPIC and msg.payload.decode("utf-8") == "stop"
        ):
            _msg = "stop listening sensor data"
            logger.info(_msg)
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.unsubscribe(PROCESS_CONTROL_TOPIC)
            import_sensor_data(mysql_config)
            client.publish(IMPORT_SENSOR_TOPIC, json.dumps({"process_id": process_id}))
            client.disconnect()

    client.on_message = on_message
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()
