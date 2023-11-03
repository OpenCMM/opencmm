import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import requests
import xml.etree.ElementTree as ET
import mysql.connector
import threading
from . import status, hakaru, mt
from cnceye.edge import find
from cncmark import arc, pair
import logging
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


chunk_size = 1024
xyz = None
done = False
data_to_insert = []
USERNAME = "opencmm"
PASSWORD = "opencmm"


def listen_sensor(mqtt_url: str, process_id: int):
    global data_to_insert
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    receive_data_topic = "sensor/data"

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        logger.info("receive_sensor_data(): connected")
        client.subscribe(receive_data_topic)

    client.on_connect = on_connect

    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        while not done:
            distance = float(msg.payload.decode("utf-8"))
            if xyz is not None:
                (x, y, z) = xyz
                data_to_insert.append((x, y, z, process_id, distance))

    client.on_message = on_message
    client.connect(mqtt_url, 1883, 60)


def control_sensor_status(
    mqtt_url: str,
    mysql_config: dict,
    process_id: int,
    model_id: int,
    final_coordinates: tuple,
    streaming_config: tuple,
):
    global done
    control_sensor_topic = "sensor/control"

    def is_same_coord(target_coord, current_coord):
        return (
            target_coord[0] == current_coord[0] and target_coord[1] == current_coord[1]
        )

    # send config to sensor
    logger.info("send config to sensor")
    (interval, threshold) = streaming_config
    publish.single(
        control_sensor_topic,
        hakaru.send_config(interval, threshold),
        hostname=mqtt_url,
        auth={"username": USERNAME, "password": PASSWORD},
    )

    while not done:
        sleep(1)
        if xyz is not None and is_same_coord(final_coordinates, xyz):
            logger.info("ready to stop streaming")
            publish.single(
                control_sensor_topic,
                hakaru.deep_sleep(),
                hostname=mqtt_url,
                auth={"username": USERNAME, "password": PASSWORD},
            )
            logger.info("stop streaming")
            done = True

            try:
                combine_data(mysql_config)
                logger.info("data combined")
                status.update_process_status(mysql_config, process_id, "data combined")
            except Exception as e:
                logger.warning(e)
                status.update_process_status(
                    mysql_config, process_id, "Error at combine_data()", str(e)
                )

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
                    break
                find.add_measured_edge_coord(update_list, mysql_config)
                logger.info(f"{edge_count} edges found")
                pair.add_line_length(mysql_config)
                arc.add_measured_arc_info(model_id, mysql_config)
            except Exception as e:
                logger.warning(e)
                status.update_process_status(
                    mysql_config, process_id, "Error at find_edges()", str(e)
                )

            status.update_process_status(mysql_config, process_id, "done")
            logger.info("done")


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
    mqtt_url: str,
    mysql_config: dict,
    mtconnect_config: tuple,
    process_id: int,
    model_id: int,
    final_coordinates: tuple,
    streaming_config: tuple,
):
    thread1 = threading.Thread(
        target=listen_sensor,
        args=(
            (
                mqtt_url,
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
                mqtt_url,
                mysql_config,
                process_id,
                model_id,
                final_coordinates,
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
