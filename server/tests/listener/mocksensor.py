import paho.mqtt.client as mqtt
import json
from server.config import (
    CONTROL_SENSOR_TOPIC,
    MQTT_BROKER_URL,
    MQTT_PASSWORD,
    MQTT_USERNAME,
    MYSQL_CONFIG,
    RECEIVE_DATA_TOPIC,
)
from server.measure.sensor import get_sensor_data


def save_sensor_data_as_csv(process_id: int, destination_file: str):
    sensor_data = get_sensor_data(process_id, MYSQL_CONFIG)
    # remove id, process_id
    sensor_data = [row[2:] for row in sensor_data]
    # save as csv
    with open(f"tests/fixtures/csv/{destination_file}", "w") as f:
        for row in sensor_data:
            f.write(",".join(map(str, row)) + "\n")


def start_mock_sensor(sensor_csv_path: str):
    sensor_data = []

    with open(sensor_csv_path, "r") as f:
        sensor_data = f.readlines()

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        client.subscribe(RECEIVE_DATA_TOPIC)
        client.subscribe(CONTROL_SENSOR_TOPIC)

    def on_message(client, userdata, msg):
        msg_payload = msg.payload.decode("utf-8")
        if msg.topic == CONTROL_SENSOR_TOPIC and msg_payload == "stop":
            client.unsubscribe(RECEIVE_DATA_TOPIC)
            client.disconnect()
            client.loop_stop()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, 1883, 60)
    client.loop_start()

    for row in sensor_data:
        sensor_output = row[:-1].split(",")[2]
        timestamp = row[:-1].split(",")[1]
        unix_timestamp = int(timestamp)
        mills = unix_timestamp * 1000
        data = json.dumps(
            {
                "timestamp": timestamp,
                "mills": mills,
                "data": sensor_output,
            }
        )
        client.publish(RECEIVE_DATA_TOPIC, data)
