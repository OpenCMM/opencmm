import json
from datetime import datetime
from server.config import get_config
import logging
from server.listener.mt.reader import import_mtconnect_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


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
