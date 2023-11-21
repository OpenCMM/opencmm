import threading
from server.config import (
    MQTT_BROKER_URL,
    get_config,
)
from . import hakaru, mt
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def listener_start(
    mysql_config: dict,
    process_id: int,
):
    conf = get_config()
    mtconnect_interval = conf["mtconnect"]["interval"]
    sensor_interval = conf["sensor"]["interval"]
    sensor_threshold = conf["sensor"]["threshold"]

    thread1 = threading.Thread(
        target=hakaru.listen_sensor,
        args=(
            (
                MQTT_BROKER_URL,
                process_id,
                mysql_config,
                (sensor_interval, sensor_threshold),
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
