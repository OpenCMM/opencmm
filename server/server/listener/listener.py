import paho.mqtt.client as mqtt
import requests
import xml.etree.ElementTree as ET
import mysql.connector
import threading
from server.config import (
    CONTROL_SENSOR_TOPIC,
    LISTENER_LOG_TOPIC,
    MQTT_BROKER_URL,
    MQTT_PASSWORD,
    MQTT_USERNAME,
    PROCESS_CONTROL_TOPIC,
    RECEIVE_DATA_TOPIC,
)
from . import status, hakaru, mt
from cnceye.edge import find
from server.mark import arc, pair
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


chunk_size = 1024
xyz = None
done = False
data_to_insert = []


def listen_sensor(mqtt_url: str, process_id: int):
    global data_to_insert
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        logger.info("receive_sensor_data(): connected")
        client.subscribe(RECEIVE_DATA_TOPIC)
        client.subscribe(PROCESS_CONTROL_TOPIC)

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        if msg.topic == RECEIVE_DATA_TOPIC:
            distance = float(msg.payload.decode("utf-8"))
            if xyz is not None:
                (x, y, z) = xyz
                data_to_insert.append((x, y, z, process_id, distance))

        elif (
            msg.topic == PROCESS_CONTROL_TOPIC and msg.payload.decode("utf-8") == "stop"
        ):
            _msg = "stop listening sensor data"
            logger.info(_msg)
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.unsubscribe(PROCESS_CONTROL_TOPIC)
            client.disconnect()

    client.on_message = on_message
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()


def control_sensor_status(
    mqtt_url: str,
    mysql_config: dict,
    process_id: int,
    model_id: int,
    streaming_config: tuple,
):
    global done

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        logger.info("control_sensor_status(): connected")

        # send config to sensor
        (interval, threshold) = streaming_config
        client.publish(CONTROL_SENSOR_TOPIC, hakaru.send_config(interval, threshold))
        logger.info("sent config to sensor")

        client.subscribe(PROCESS_CONTROL_TOPIC)

    def on_message(client, userdata, msg):
        global done
        msg_payload = msg.payload.decode("utf-8")
        logger.info(msg.topic + " " + msg_payload)

        def disconnect_and_publish_log(_msg: str):
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.unsubscribe(PROCESS_CONTROL_TOPIC)
            client.disconnect()
            client.loop_stop()

        if msg_payload == "stop":
            logger.info("stop measurement")
            done = True

            try:
                combine_data(mysql_config)
                _status = "data combined"
                logger.info(_status)
                client.publish(LISTENER_LOG_TOPIC, _status)
            except Exception as e:
                logger.warning(e)
                status.update_process_status(
                    mysql_config, process_id, "Error at combine_data()", str(e)
                )
                disconnect_and_publish_log("Error at combine_data()" + str(e))
                return

            try:
                measured_edges = find.find_edges(process_id, mysql_config=mysql_config)
                edge_data = find.get_edge_data(model_id, mysql_config)
                # distance_threshold should be passed as an argument
                update_list = find.identify_close_edge(edge_data, measured_edges)
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
                pair.add_line_length(mysql_config)
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
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()


def combine_data(mysql_config: dict):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    mysql_cur.executemany(
        "INSERT INTO sensor(x, y, z, process_id, distance) VALUES (%s,%s,%s, %s, %s)",
        data_to_insert,
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


def mtconnect_streaming_reader(
    mtconnect_config: tuple, mysql_config: dict, process_id: int
):
    global xyz
    (url, interval) = mtconnect_config
    endpoint = f"{url}&interval={interval}"
    try:
        response = requests.get(endpoint, stream=True)
        xml_buffer = ""
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                if done:
                    break

                raw_data = chunk.decode("utf-8")
                # print(raw_data)
                if mt.is_first_chunk(raw_data):
                    # beginning of xml
                    xml_string = mt.remove_http_response_header(raw_data)
                    xml_buffer = xml_string

                    if mt.is_last_chunk(raw_data):
                        try:
                            xyz = mt.get_coordinates(xml_buffer)[:3]
                        except ET.ParseError:
                            pass
                else:
                    xml_buffer += raw_data
                    if not mt.is_last_chunk(raw_data):
                        continue

                    # full xml data received
                    try:
                        xyz = mt.get_coordinates(xml_buffer)[:3]
                    except ET.ParseError:
                        err_msg = "ParseError"
                        logger.warning(err_msg)
                        status.update_process_status(
                            mysql_config, process_id, err_msg, err_msg
                        )

        else:
            err_msg = f"Error: {response.status_code}"
            logger.warning(err_msg)
            status.update_process_status(mysql_config, process_id, err_msg, err_msg)

    except requests.ConnectionError:
        err_msg = "Connection to the MTConnect agent was lost."
        logger.warning(err_msg)
        status.update_process_status(mysql_config, process_id, err_msg, err_msg)
    except KeyboardInterrupt:
        _msg = "Streaming stopped by user."
        logger.info(_msg)
        status.update_process_status(mysql_config, process_id, _msg)


def listener_start(
    mysql_config: dict,
    mtconnect_config: tuple,
    process_id: int,
    model_id: int,
    streaming_config: tuple,
):
    thread1 = threading.Thread(
        target=listen_sensor,
        args=(
            (
                MQTT_BROKER_URL,
                process_id,
            )
        ),
    )
    thread2 = threading.Thread(
        target=mtconnect_streaming_reader,
        args=(
            (
                mtconnect_config,
                mysql_config,
                process_id,
            )
        ),
    )
    thread3 = threading.Thread(
        target=control_sensor_status,
        args=(
            (
                MQTT_BROKER_URL,
                mysql_config,
                process_id,
                model_id,
                streaming_config,
            )
        ),
    )

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Join the threads (optional, to wait for them to finish)
    thread1.join()
    thread2.join()
    thread3.join()
