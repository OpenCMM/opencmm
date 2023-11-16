import threading
from server.config import (
    MQTT_BROKER_URL,
)
from . import hakaru, mt
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def listener_start(
    mysql_config: dict,
    mtconnect_interval: int,
    process_id: int,
    streaming_config: tuple,
):
    thread1 = threading.Thread(
        target=hakaru.listen_sensor,
        args=(
            (
                MQTT_BROKER_URL,
                process_id,
                mysql_config,
                streaming_config,
            )
        ),
    )
    thread2 = threading.Thread(
        target=mt.mtconnect_streaming_reader,
        args=(
            (
                mtconnect_interval,
                mysql_config,
                process_id,
                MQTT_BROKER_URL,
            )
        ),
    )
    thread3 = threading.Thread(
        target=mt.stop_mtconnect_reader,
        args=((MQTT_BROKER_URL,)),
    )

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Join the threads (optional, to wait for them to finish)
    thread1.join()
    thread2.join()
    thread3.join()
