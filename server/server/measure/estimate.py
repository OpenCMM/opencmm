import paho.mqtt.client as mqtt
from server.listener import status
from datetime import datetime, timedelta
from server.config import (
    GCODE_PATH,
    LISTENER_LOG_TOPIC,
    MQTT_BROKER_URL,
    MQTT_PASSWORD,
    MQTT_USERNAME,
    get_config,
)
from server.mark.edge import (
    import_edge_results,
    get_edge_id_from_line_number,
    delete_edge_results,
)
from server.prepare import get_gcode_filename
from .sensor import get_sensor_data
from server.model import get_model_data
import numpy as np
from .gcode import (
    load_gcode,
    get_start_end_points_from_line_number,
    get_timestamp_at_point,
    get_true_line_number,
)
from .mtconnect import get_mtconnect_data
from server.mark import arc, pair
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def sensor_timestamp_to_coord(
    start_timestamp: datetime,
    sensor_timestamp: datetime,
    xy: tuple,
    direction_vector: tuple,
    feedrate: float,
    beam_diameter: float,  # in μm
):
    """
    Estimate the coordinate of the edge from sensor timestamp
    """
    timestamp_diff = sensor_timestamp - start_timestamp
    distance = feedrate * timestamp_diff.total_seconds()
    direction_vector = np.array(direction_vector)
    distance_with_beam_diameter = distance + beam_diameter / 1000  # convert to mm
    coord = np.array(xy) + distance_with_beam_diameter * direction_vector
    # round to 3 decimal places
    coord = np.round(coord, 3)
    return tuple(coord)


def update_data_after_measurement(
    mysql_config: dict,
    process_id: int,
    model_id: int,
):
    """
    Estimate edges from mtconnect data and sensor data
    """
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))

    def on_message(client, userdata, msg):
        msg_payload = msg.payload.decode("utf-8")
        logger.info(msg.topic + " " + msg_payload)

    def disconnect_and_publish_log(_msg: str):
        client.publish(LISTENER_LOG_TOPIC, _msg)
        client.disconnect()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_URL, 1883, 60)

    update_list = compute_edge_results(mysql_config, model_id, process_id)
    edge_count = len(update_list)
    if edge_count == 0:
        status.update_process_status(
            mysql_config,
            process_id,
            "Error at update_data_after_measurement()",
            "No edge found",
        )
        disconnect_and_publish_log("No edge found")
        return
    import_edge_results(update_list, mysql_config)

    _msg = f"{edge_count} edges found"
    logger.info(_msg)
    client.publish(LISTENER_LOG_TOPIC, _msg)

    try:
        pair.add_line_length(model_id, mysql_config, process_id)
        arc.add_measured_arc_info(model_id, mysql_config, process_id)
        status.update_process_status(mysql_config, process_id, "done")
        logger.info("done")
        disconnect_and_publish_log("done")
    except Exception as e:
        logger.warning(e)
        status.update_process_status(
            mysql_config, process_id, "Error at update_data_after_measurement()", str(e)
        )
        disconnect_and_publish_log(str(e))


def compute_edge_results(mysql_config: dict, model_id: int, process_id: int):
    conf = get_config()
    mtconnect_latency = conf["mtconnect"]["latency"]
    beam_diameter = conf["sensor"]["beam_diameter"]
    model_row = get_model_data(model_id)
    filename = model_row[1]
    # offset = (model_row[3], model_row[4], model_row[5])
    gcode_filename = get_gcode_filename(filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode = load_gcode(gcode_file_path)
    mtconnect_data = get_mtconnect_data(process_id, mysql_config)
    np_mtconnect_data = np.array(mtconnect_data)
    z = np_mtconnect_data[0][5]
    sensor_data = get_sensor_data(process_id, mysql_config)
    np_sensor_data = np.array(sensor_data)

    current_line = 0
    update_list = []
    for row in np_mtconnect_data:
        xy = (row[3], row[4])
        line = int(row[6])
        line = get_true_line_number(xy, line, gcode)
        if not line:
            # Not on line
            continue
        if line % 2 != 0:
            # Not measuring
            continue

        if line == current_line:
            continue

        _timestamp = row[2] - timedelta(milliseconds=mtconnect_latency)
        # feedrate = row[7] # feedrate from MTConnect is not accurate
        (start, end, feedrate) = get_start_end_points_from_line_number(gcode, line)
        # get timestamp at start and end
        start_timestamp = get_timestamp_at_point(xy, start, feedrate, _timestamp, True)
        end_timestamp = get_timestamp_at_point(xy, end, feedrate, _timestamp, False)

        # get sensor data that is between start and end timestamp
        for sensor_row in np_sensor_data:
            sensor_timestamp = sensor_row[2]
            if start_timestamp <= sensor_timestamp <= end_timestamp:
                direction_vector = np.array([end[0] - start[0], end[1] - start[1]])
                distance = np.linalg.norm(direction_vector)
                direction_vector = tuple(direction_vector / distance)
                edge_coord = sensor_timestamp_to_coord(
                    start_timestamp,
                    sensor_timestamp,
                    start,
                    direction_vector,
                    feedrate,
                    beam_diameter,
                )
                edge_id = get_edge_id_from_line_number(mysql_config, model_id, line)
                update_list.append(
                    (edge_id, process_id, edge_coord[0], edge_coord[1], z)
                )
                # ignore the rest of the sensor data
                # multiple edges can be measured due to the following reasons:
                # - noise (can be reduced by increasing the sensor threshold)
                # - sensor restart
                # - timestamp is not accurate
                break

        current_line = line
    return update_list


def recompute(mysql_config: dict, process_id: int):
    # remove previous results
    delete_edge_results(mysql_config, process_id)
    arc.delete_measured_arc_info(mysql_config, process_id)
    pair.delete_measured_length(mysql_config, process_id)

    process_data = status.get_process_status(mysql_config, process_id)
    model_id = process_data[1]
    update_list = compute_edge_results(mysql_config, model_id, process_id)

    edge_count = len(update_list)
    if edge_count == 0:
        status.update_process_status(
            mysql_config,
            process_id,
            "Error at update_data_after_measurement()",
            "No edge found",
        )
        return
    import_edge_results(update_list, mysql_config)

    _msg = f"{edge_count} edges found"
    logger.info(_msg)

    try:
        pair.add_line_length(model_id, mysql_config, process_id)
        arc.add_measured_arc_info(model_id, mysql_config, process_id)
        status.update_process_status(mysql_config, process_id, "done")
        logger.info("done")
    except Exception as e:
        logger.warning(e)
        status.update_process_status(
            mysql_config, process_id, "Error at update_data_after_measurement()", str(e)
        )
