import requests
import xml.etree.ElementTree as ET
import mysql.connector
import logging
from server.config import (
    LISTENER_LOG_TOPIC,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    PROCESS_CONTROL_TOPIC,
)
from .parse import (
    is_first_chunk,
    remove_http_response_header,
    is_last_chunk,
)
from server.listener import status
import paho.mqtt.client as mqtt
from .parse import mtconnect_table_row_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


chunk_size = 1024
done = False
mt_data_list = []


def stop_mtconnect_reader(
    mqtt_url: str,
):
    global done

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))
        client.subscribe(PROCESS_CONTROL_TOPIC)

    def on_message(client, userdata, msg):
        global done
        if msg.topic == PROCESS_CONTROL_TOPIC and msg.payload.decode("utf-8") == "stop":
            _msg = "stop listening mtconnect"
            logger.info(_msg)
            client.publish(LISTENER_LOG_TOPIC, _msg)
            client.unsubscribe(PROCESS_CONTROL_TOPIC)
            client.disconnect()
            done = True

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_url, 1883, 60)
    client.loop_start()


def import_mtconnect_data(mysql_config: dict):
    # Perform a bulk insert
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()

    query = (
        "INSERT INTO mtconnect(process_id, timestamp, "
        "x, y, z, line, feedrate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    mysql_cur.executemany(
        query,
        mt_data_list,
    )
    mysql_conn.commit()

    mysql_cur.close()
    mysql_conn.close()


def mtconnect_streaming_reader(
    mtconnect_config: tuple, mysql_config: dict, process_id: int
):
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
                    import_mtconnect_data(mysql_config)
                    break

                raw_data = chunk.decode("utf-8")
                if is_first_chunk(raw_data):
                    # beginning of xml
                    xml_string = remove_http_response_header(raw_data)
                    xml_buffer = xml_string

                    if is_last_chunk(raw_data):
                        try:
                            mt_data_list.append(
                                mtconnect_table_row_data(xml_buffer, process_id)
                            )
                        except ET.ParseError:
                            pass
                else:
                    xml_buffer += raw_data
                    if not is_last_chunk(raw_data):
                        continue

                    # full xml data received
                    try:
                        mt_data_list.append(
                            mtconnect_table_row_data(xml_buffer, process_id)
                        )
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
