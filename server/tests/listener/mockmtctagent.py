import paho.mqtt.client as mqtt
import json
from server.config import (
    MQTT_PASSWORD,
    MQTT_USERNAME,
    PROCESS_CONTROL_TOPIC,
    MQTT_BROKER_URL,
    get_config,
    MYSQL_CONFIG,
)
from server.measure.mtconnect import get_mtconnect_data
from time import sleep


class MockMtctAgent:
    def __init__(self, mqtt_log_path: str):
        self.config = get_config()
        self.device = self.config["mtconnect"]["device"]
        self.topic = f"MTConnect/Current/{self.device}"
        with open(mqtt_log_path) as f:
            data = json.load(f)
            msgs = data[0]["messages"]
            self.msgs = msgs

        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client = client

        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.topic)
            client.subscribe(PROCESS_CONTROL_TOPIC)

        client.on_connect = on_connect
        client.connect(MQTT_BROKER_URL, 1883, 60)
        client.loop_start()

    def start(self):
        for msg in self.msgs:
            self.client.publish(self.topic, msg["payload"])
            sleep(0.1)

        self.client.publish(PROCESS_CONTROL_TOPIC, "stop")
        self.client.unsubscribe(self.topic)
        self.client.disconnect()


def start_mock_mtct_agent(mqtt_log_path: str):
    mock_mtct_agent = MockMtctAgent(mqtt_log_path)
    mock_mtct_agent.start()


def save_mtct_data_as_csv(process_id: int, destination_file: str):
    mtct_data = get_mtconnect_data(process_id, MYSQL_CONFIG)
    # remove id, process_id
    mtct_data = [row[2:] for row in mtct_data]
    # save as csv
    with open(f"tests/fixtures/csv/mtct/{destination_file}", "w") as f:
        for row in mtct_data:
            f.write(",".join(map(str, row)) + "\n")
