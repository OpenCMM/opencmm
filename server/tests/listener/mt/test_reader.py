from server.config import MYSQL_CONFIG
from server.listener.mt import mtconnect_streaming_reader, stop_mtconnect_reader
import threading
import pytest

MQTT_BROKER_URL = "192.168.10.104"


@pytest.mark.skip(reason="No MQTT broker running")
def test_mtconnect_streaming_reader():
    # mtconnect_url = (
    # 	"http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems"
    # )
    mtconnect_url = "https://demo.metalogi.io/current?path=//Components"
    # mtconnect_url = "https://demo.metalogi.io/current?path=//Axes/Components/Linear/DataItems/DataItem"

    interval = 200
    mtconnect_config = (mtconnect_url, interval)

    thread1 = threading.Thread(
        target=mtconnect_streaming_reader,
        args=(
            (
                mtconnect_config,
                MYSQL_CONFIG,
                1,
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
