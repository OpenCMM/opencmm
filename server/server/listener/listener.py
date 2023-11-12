import paho.mqtt.client as mqtt
import threading
from server.config import (
    LISTENER_LOG_TOPIC,
    MQTT_BROKER_URL,
    MQTT_PASSWORD,
    MQTT_USERNAME,
)
from . import status, hakaru, mt
from server import find
from server.model import get_model_data
from server.mark import arc, pair
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


chunk_size = 1024
done = False
mt_data_list = []


def update_data_after_measurement(
    mysql_config: dict,
    process_id: int,
    model_id: int,
):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))

    def on_message(client, userdata, msg):
        global done
        msg_payload = msg.payload.decode("utf-8")
        logger.info(msg.topic + " " + msg_payload)

        def disconnect_and_publish_log(_msg: str):
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.disconnect()
            client.loop_stop()

        try:
            measured_edges = find.find_edges(process_id, mysql_config)
            edge_data = find.get_edge_data(model_id, mysql_config)
            _model_data = get_model_data(model_id)
            _offset = (_model_data[3], _model_data[4], _model_data[5])
            # distance_threshold should be passed as an argument
            update_list = find.identify_close_edge(edge_data, measured_edges, _offset)
            edge_count = len(update_list)
            if edge_count == 0:
                status.update_process_status(
                    mysql_config,
                    process_id,
                    "Error at find_edges()",
                    "No edge found",
                )
                disconnect_and_publish_log("Error at find_edges(): No edge found")
                return
            find.add_measured_edge_coord(update_list, mysql_config)
            _msg = f"{edge_count} edges found"
            logger.info(_msg)
            client.publish(LISTENER_LOG_TOPIC, _msg)
            pair.add_line_length(model_id, mysql_config)
            arc.add_measured_arc_info(model_id, mysql_config)
            status.update_process_status(mysql_config, process_id, "done")
            logger.info("done")
            disconnect_and_publish_log("done")
        except Exception as e:
            logger.warning(e)
            status.update_process_status(
                mysql_config, process_id, "Error at find_edges()", str(e)
            )
            disconnect_and_publish_log("Error at find_edges()" + str(e))

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, 1883, 60)
    client.loop_start()


def listener_start(
    mysql_config: dict,
    mtconnect_config: tuple,
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
                mtconnect_config,
                mysql_config,
                process_id,
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
