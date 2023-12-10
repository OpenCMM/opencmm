import paho.mqtt.client as mqtt
from server.listener import status
from datetime import datetime, timedelta
from server.config import (
    GCODE_PATH,
    LISTENER_LOG_TOPIC,
    MODEL_PATH,
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
from server.mark.gcode import get_gcode_filename
from .sensor import get_sensor_data, sensor_output_to_mm
from server.model import get_model_data
import numpy as np
from .gcode import (
    load_gcode,
    get_start_end_points_from_line_number,
)
from .mtconnect import MtctDataChecker
from server.mark import arc, pair
from server.mark.trace import (
    get_trace_line_id_from_line_number,
    delete_trace_line_results,
)
from server.mark.trace import import_trace_line_results
import logging
from scipy.ndimage import uniform_filter1d
import trimesh

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class Result:
    def __init__(self, mysql_config: dict, model_id: int, process_id: int):
        self.mysql_config = mysql_config
        self.model_id = model_id
        self.process_id = process_id
        self.conf = get_config()

        self.mtct_data_checker = MtctDataChecker(mysql_config, model_id, process_id)
        self.mtct_lines = self.mtct_data_checker.estimate_timestamps_from_mtct_data()
        sensor_data = get_sensor_data(process_id, mysql_config)
        self.np_sensor_data = np.array(sensor_data)

        model_row = get_model_data(model_id)
        filename = model_row[1]
        self.stl_filepath = f"{MODEL_PATH}/{filename}"
        self.mesh = trimesh.load(self.stl_filepath)
        self.offset = (model_row[3], model_row[4], model_row[5])
        gcode_filename = get_gcode_filename(filename)
        gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
        self.gcode = load_gcode(gcode_file_path)
        self.z = self.mtct_data_checker.np_mtconnect_data[0][5]
        self.first_line_for_tracing = self.mtct_data_checker.first_line_for_tracing

    def sensor_timestamp_to_coord(
        self,
        start_timestamp: datetime,
        sensor_timestamp: datetime,
        xy: tuple,
        direction_vector: tuple,
        feedrate: float,
    ):
        """
        Estimate the coordinate of the edge from sensor timestamp
        """
        beam_diameter = self.conf["sensor"]["beam_diameter"]  # in μm
        sensor_response_time = self.conf["sensor"]["response_time"]  # in ms
        # factor in sensor response time
        sensor_timestamp -= timedelta(milliseconds=sensor_response_time)
        timestamp_diff = sensor_timestamp - start_timestamp
        distance = feedrate * timestamp_diff.total_seconds()
        direction_vector = np.array(direction_vector)
        beam_diameter = beam_diameter / 1000  # convert to mm
        distance_with_beam_diameter = (
            distance + beam_diameter / 2
        )  # add half of beam radius
        coord = np.array(xy) + distance_with_beam_diameter * direction_vector
        # round to 3 decimal places
        coord = np.round(coord, 3)
        return tuple(coord)

    def get_expected_z_value(self, xy: tuple):
        ray_origins = np.array([[xy[0] - self.offset[0], xy[1] - self.offset[1], 100]])
        ray_directions = np.array([[0, 0, -1]])
        locations = self.mesh.ray.intersects_location(
            ray_origins=ray_origins, ray_directions=ray_directions
        )[0]
        if len(locations) == 0:
            return None
        # location with the highest z value is the closest point
        location = locations[np.argmax(locations[:, 2])]
        return location[2] + self.offset[2]

    def validate_sensor_output(self, sensor_output: float, start: tuple, end: tuple):
        measured_z = sensor_output_to_mm(sensor_output)
        edge_xy = (np.array(start) + np.array(end)) / 2
        expected_z = self.get_expected_z_value(edge_xy)
        # sensor outputs >18800 when there is no workpiece in the sensor range
        if expected_z is None:
            return sensor_output > 18800
        if -35 <= expected_z <= 35:
            return abs(measured_z - expected_z) < self.conf["sensor"]["tolerance"]
        return sensor_output > 18800

    def get_edge_results(self, start_timestamp, end_timestamp, line):
        """
        Estimate the exact coordinate of the edge from mtconnect data and
        sensor data using timestamp
        """
        # feedrate = row[7] # feedrate from MTConnect is not accurate
        (start, end, feedrate) = get_start_end_points_from_line_number(self.gcode, line)

        # get sensor data that is between start and end timestamp
        for sensor_row in self.np_sensor_data:
            sensor_timestamp = sensor_row[2]
            sensor_output = sensor_row[3]
            if sensor_row[0] == 2:
                pass
            if start_timestamp <= sensor_timestamp <= end_timestamp:
                if not self.validate_sensor_output(sensor_output, start, end):
                    continue
                direction_vector = np.array([end[0] - start[0], end[1] - start[1]])
                distance = np.linalg.norm(direction_vector)
                direction_vector = tuple(direction_vector / distance)
                edge_coord = self.sensor_timestamp_to_coord(
                    start_timestamp,
                    sensor_timestamp,
                    start,
                    direction_vector,
                    feedrate,
                )
                # when edges are overlapping, multiple edges can be measured
                # for a single line
                edge_ids = get_edge_id_from_line_number(
                    self.mysql_config, self.model_id, line
                )
                # ignore the rest of the sensor data
                # multiple edges can be measured due to the following reasons:
                # - noise (can be reduced by increasing the sensor threshold)
                # - sensor restart
                # - timestamp is not accurate
                results = []
                for edge_id in edge_ids:
                    results.append(
                        (
                            edge_id,
                            self.process_id,
                            edge_coord[0],
                            edge_coord[1],
                            self.z,
                        )
                    )
                return results

    def get_trace_line_result(self, start_timestamp, end_timestamp, line):
        """
        Estimate the approximate distance between the workpiece and the sensor
        """
        distance_results = []
        # get sensor data that is between start and end timestamp
        for sensor_row in self.np_sensor_data:
            sensor_timestamp = sensor_row[2]
            if start_timestamp <= sensor_timestamp <= end_timestamp:
                distance_results.append(sensor_row[3])

        # Apply moving average filter to remove fluctuations
        filtered_distance_results = uniform_filter1d(distance_results, size=5)

        average_sensor_output = np.mean(filtered_distance_results)

        if len(filtered_distance_results) == 0:
            return
        trace_line_id = get_trace_line_id_from_line_number(
            self.mysql_config, self.model_id, line
        )
        return [trace_line_id, self.process_id, average_sensor_output]

    def compute_updating_data(self):
        current_line = 0
        edge_update_list = []
        trace_line_update_list = []
        for mtct_line in self.mtct_lines:
            line_number = mtct_line[0]
            start_timestamp = mtct_line[1]
            end_timestamp = mtct_line[2]

            if line_number == current_line:
                continue

            # Edge detection
            if (
                not self.first_line_for_tracing
                or line_number < self.first_line_for_tracing - 2
            ):
                if line_number % 2 != 0:
                    # Not measuring
                    continue

                edge_results = self.get_edge_results(
                    start_timestamp, end_timestamp, line_number
                )
                if edge_results:
                    edge_update_list += edge_results

            # waiting
            elif line_number == self.first_line_for_tracing - 2:
                continue

            # tracing
            else:
                if line_number % 2 == 0:
                    # Not measuring
                    continue
                trace_line_result = self.get_trace_line_result(
                    start_timestamp, end_timestamp, line_number
                )
                if trace_line_result:
                    trace_line_update_list.append(trace_line_result)

            current_line = line_number

        return edge_update_list, trace_line_update_list


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

    result = Result(mysql_config, model_id, process_id)
    edge_update_list, trace_line_update_list = result.compute_updating_data()
    edge_count = len(edge_update_list)
    if edge_count == 0:
        status.update_process_status(
            mysql_config,
            process_id,
            "Error at update_data_after_measurement()",
            "No edge found",
        )
        disconnect_and_publish_log("No edge found")
        return
    import_edge_results(edge_update_list, mysql_config)
    if trace_line_update_list:
        import_trace_line_results(mysql_config, trace_line_update_list)

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


def recompute(mysql_config: dict, process_id: int):
    # remove previous results
    delete_edge_results(mysql_config, process_id)
    arc.delete_measured_arc_info(mysql_config, process_id)
    pair.delete_measured_length(mysql_config, process_id)
    delete_trace_line_results(mysql_config, process_id)

    process_data = status.get_process_status(mysql_config, process_id)
    model_id = process_data[1]
    result = Result(mysql_config, model_id, process_id)
    edge_update_list, trace_line_update_list = result.compute_updating_data()

    edge_count = len(edge_update_list)
    if edge_count == 0:
        status.update_process_status(
            mysql_config,
            process_id,
            "Error at update_data_after_measurement()",
            "No edge found",
        )
        return
    import_edge_results(edge_update_list, mysql_config)
    if trace_line_update_list:
        import_trace_line_results(mysql_config, trace_line_update_list)

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
