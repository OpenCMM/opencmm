import json
from datetime import datetime
from server.config import (
    IMPORT_MTCONNECT_TOPIC,
    LISTENER_LOG_TOPIC,
    MQTT_PASSWORD,
    MQTT_USERNAME,
    PROCESS_CONTROL_TOPIC,
    get_config,
)
import logging
import paho.mqtt.client as mqtt
from server.listener.mt.reader import import_mtconnect_data
from . import status

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class MtqqParseError(Exception):
    pass


class MqttListener:
    def __init__(self, mysql_config: dict, process_id: int):
        self.mysql_config = mysql_config
        self.process_id = process_id
        self.config = get_config()
        self.device = self.config["mtconnect"]["device"]
        self.topic = f"MTConnect/Current/{self.device}"

    def remove_unavailable_data(self, mt_data_list: list):
        # remove unavailable data
        update_data_list = []
        for mt_data in mt_data_list:
            if None in mt_data:
                continue
            if "UNAVAILABLE" in mt_data:
                continue
            update_data_list.append(mt_data)
        return update_data_list

    def import_mtconnect_data_from_mqtt_log(self, mqtt_log_path: str):
        update_list = []
        prev_timestamp = None
        with open(mqtt_log_path) as f:
            data = json.load(f)
            msgs = data[0]["messages"]
            count = 0
            idx = 0
            for msg in msgs:
                topic = msg["topic"]
                if topic != self.topic:
                    continue
                try:
                    payload = json.loads(msg["payload"])
                except json.decoder.JSONDecodeError:
                    continue
                if "MTConnectStreams" not in payload:
                    count += 1
                    continue

                idx += 1
                execution = None
                execution_list = payload["MTConnectStreams"]["Streams"]["DeviceStream"][
                    0
                ]["ComponentStream"][1]["Events"]["Execution"]
                for _execution in execution_list:
                    if _execution["dataItemId"] == "execution1":
                        execution = _execution
                if execution is None:
                    continue
                line = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                    "ComponentStream"
                ][9]["Events"]["Line"][0]
                feedrate = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                    "ComponentStream"
                ][9]["Samples"]["PathFeedrate"][1]
                x = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                    "ComponentStream"
                ][3]["Samples"]["Position"][0]
                y = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                    "ComponentStream"
                ][4]["Samples"]["Position"][0]
                z = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                    "ComponentStream"
                ][5]["Samples"]["Position"][0]

                all_timestamps = [
                    x["timestamp"],
                    y["timestamp"],
                    z["timestamp"],
                    # line["timestamp"],
                ]
                last_timestamp = max(all_timestamps)
                # to datetime
                last_timestamp = datetime.strptime(
                    last_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                current_row = [
                    self.process_id,
                    last_timestamp,
                    x["value"],
                    y["value"],
                    z["value"],
                    line["value"],
                    feedrate["value"],
                ]
                if prev_timestamp != last_timestamp:
                    update_list.append(current_row)
                    prev_timestamp = last_timestamp
                count += 1

        logger.info(f"count: {count}")
        update_list = self.remove_unavailable_data(update_list)
        import_mtconnect_data(self.mysql_config, update_list)

    def parse_mtct_data(self, payload: str) -> tuple:
        """
        Parse MTConnect data from MQTT payload
        """
        payload = json.loads(payload)

        if "MTConnectStreams" not in payload:
            raise MtqqParseError("MTConnectStreams not in payload")

        execution = None
        execution_list = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][1]["Events"]["Execution"]
        for _execution in execution_list:
            if _execution["dataItemId"] == "execution1":
                execution = _execution
        if execution is None:
            return None
        line = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][9]["Events"]["Line"][0]
        feedrate = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][9]["Samples"]["PathFeedrate"][1]
        x = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][3]["Samples"]["Position"][0]
        y = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][4]["Samples"]["Position"][0]
        z = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
            "ComponentStream"
        ][5]["Samples"]["Position"][0]

        all_timestamps = [
            x["timestamp"],
            y["timestamp"],
            z["timestamp"],
        ]
        last_timestamp = max(all_timestamps)
        # to datetime
        last_timestamp = datetime.strptime(last_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        line_timestamp = datetime.strptime(line["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        current_row = (
            self.process_id,
            last_timestamp,
            x["value"],
            y["value"],
            z["value"],
            line["value"],
            line_timestamp,
            feedrate["value"],
        )
        return current_row


def listen_data_with_mqtt(
    mysql_config: dict,
    process_id: int,
    mqtt_url: str,
):
    mqtt_listener = MqttListener(mysql_config, process_id)
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mt_data_list = []

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        logger.info("listen_data_with_mqtt(): connected")
        client.subscribe(mqtt_listener.topic)
        client.subscribe(PROCESS_CONTROL_TOPIC)

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        if msg.topic == mqtt_listener.topic:
            try:
                row = mqtt_listener.parse_mtct_data(msg.payload.decode("utf-8"))
                mt_data_list.append(row)
            except json.decoder.JSONDecodeError:
                logger.warning("Failed to decode JSON payload")
                status.update_process_status(
                    mysql_config,
                    process_id,
                    "parse_mtct_data(): JSONDecodeError",
                    "Failed to decode JSON payload",
                )
            except MtqqParseError as e:
                logger.warning(e)
                status.update_process_status(
                    mysql_config,
                    process_id,
                    "parse_mtct_data(): MTConnectStreams not in payload",
                    "MTConnectStreams not in payload",
                )
            except Exception as e:
                logger.warning(e)
                status.update_process_status(
                    mysql_config, process_id, "listen_data_with_mqtt() error", str(e)
                )

        elif (
            msg.topic == PROCESS_CONTROL_TOPIC and msg.payload.decode("utf-8") == "stop"
        ):
            _msg = "stop listening sensor data"
            logger.info(_msg)
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.unsubscribe(PROCESS_CONTROL_TOPIC)
            logger.info("mtconnect data imported")
            if len(mt_data_list) == 0:
                logger.warning("listen_data_with_mqtt(): No data to import")
            else:
                import_mtconnect_data(mysql_config, mt_data_list, True)
            client.publish(
                IMPORT_MTCONNECT_TOPIC, json.dumps({"process_id": process_id})
            )
            status.add_end_timestamp(mysql_config, process_id)
            client.disconnect()

    client.on_message = on_message
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()
