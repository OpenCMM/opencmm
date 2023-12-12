from server.config import MYSQL_CONFIG
from server.listener.mt import mtconnect_streaming_reader, stop_mtconnect_reader
import threading
import pytest

MQTT_BROKER_URL = "192.168.10.104"


@pytest.mark.skip(reason="No MQTT broker running")
def test_mtconnect_streaming_reader():
    mtconnect_url = "http://192.168.0.19:5000/current?path=//Components"
    # mtconnect_url = "https://demo.metalogi.io/current?path=//Components"
    # mtconnect_url = "https://demo.metalogi.io/current?path=//Axes/Components/Linear/DataItems/DataItem"

    interval = 1000
    mtconnect_config = (mtconnect_url, interval)

    thread1 = threading.Thread(
        target=mtconnect_streaming_reader,
        args=(
            (
                mtconnect_config,
                MYSQL_CONFIG,
                7,
            )
        ),
    )
    thread2 = threading.Thread(
        target=stop_mtconnect_reader,
        args=((MQTT_BROKER_URL,)),
    )

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


@pytest.mark.skip(reason="Only for local testing")
def test_import_mtconnect_data():
    import json
    from datetime import datetime

    process_id = 4
    update_list = []
    prev_timestamp = None
    with open("process6.json") as f:
        data = json.load(f)
        msgs = data[0]["messages"]
        count = 0
        idx = 0
        for msg in msgs:
            topic = msg["topic"]
            if topic != "MTConnect/Current/MITSUBISHI1":
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
            execution_list = payload["MTConnectStreams"]["Streams"]["DeviceStream"][0][
                "ComponentStream"
            ][1]["Events"]["Execution"]
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
                line["timestamp"],
            ]
            # all_timestamps = [x['timestamp'], y['timestamp'], z['timestamp']]
            last_timestamp = max(all_timestamps)
            # to datetime
            last_timestamp = datetime.strptime(last_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            current_row = [
                process_id,
                last_timestamp,
                x["value"],
                y["value"],
                z["value"],
                line["value"],
                line["timestamp"],
                feedrate["value"],
            ]
            current_row = [
                process_id,
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

    print(f"count: {count}")
    # import_mtconnect_data(MYSQL_CONFIG, update_list)
