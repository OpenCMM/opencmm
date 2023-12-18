import paho.mqtt.client as mqtt
from server.listener import status
from server.config import (
    LISTENER_LOG_TOPIC,
    MQTT_BROKER_URL,
    MQTT_PASSWORD,
    MQTT_USERNAME,
)
from time import time
from server.mark.edge import (
    import_edge_results,
    delete_edge_results,
)
from .sensor import sensor_output_to_mm
import numpy as np
from .gcode import (
    get_start_end_points_from_line_number,
)
from .mtconnect import MtctDataChecker, update_mtct_latency
from server.mark import arc, pair
from server.mark.trace import (
    get_trace_line_id_from_line_number,
    delete_trace_line_results,
)
from server.mark.trace import import_trace_line_results
import logging
from scipy.ndimage import uniform_filter1d

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class Result:
    def __init__(self, mysql_config: dict, model_id: int, process_id: int):
        self.mysql_config = mysql_config
        self.model_id = model_id
        self.process_id = process_id

        self.mtct_data_checker = MtctDataChecker(mysql_config, model_id, process_id)
        self.mtct_lines = self.mtct_data_checker.estimate_timestamps_from_mtct_data()
        # self.mtct_lines = self.mtct_data_checker.adjust_delays(mtct_lines)
        self.np_sensor_data = np.array(self.mtct_data_checker.sensor_data)
        self.first_line_for_tracing = self.mtct_data_checker.first_line_for_tracing

    def get_edge_results(self, start_timestamp, end_timestamp, line):
        """
        Estimate the exact coordinate of the edge from mtconnect data and
        sensor data using timestamp
        """
        # feedrate = row[7] # feedrate from MTConnect is not accurate
        (start, end, feedrate) = get_start_end_points_from_line_number(
            self.mtct_data_checker.gcode, line
        )

        # get sensor data that is between start and end timestamp
        sensor_data_during_line = self.np_sensor_data[
            np.logical_and(
                self.np_sensor_data[:, 2] >= start_timestamp,
                self.np_sensor_data[:, 2] <= end_timestamp,
            )
        ]
        for sensor_row in sensor_data_during_line:
            sensor_timestamp = sensor_row[2]
            sensor_output = sensor_row[3]
            (
                sensor_output_valid,
                edge_ids,
            ) = self.mtct_data_checker.validate_sensor_output(sensor_output, line)
            if not sensor_output_valid:
                continue
            edge_coord = self.mtct_data_checker.sensor_timestamp_to_coord(
                start_timestamp,
                sensor_timestamp,
                start,
                end,
                feedrate,
            )
            """
            when edges are overlapping, multiple edges can be measured
            for a single line
            """
            # edge_ids = get_edge_id_from_line_number(
            #     self.mysql_config, self.model_id, line
            # )

            # ignore the rest of the sensor data
            # multiple edges can be measured due to the following reasons:
            # - noise (can be reduced by increasing the sensor threshold)
            # - sensor restart
            # - timestamp is not accurate
            results = []
            measured_z = round(sensor_output_to_mm(sensor_output), 3)
            for edge_id in edge_ids:
                results.append(
                    (
                        edge_id,
                        self.process_id,
                        edge_coord[0],
                        edge_coord[1],
                        measured_z,
                    )
                )
            return results

    def get_trace_line_result(self, start_timestamp, end_timestamp, line):
        """
        Estimate the approximate distance between the workpiece and the sensor
        """
        # get sensor data that is between start and end timestamp
        sensor_data_during_line = self.np_sensor_data[
            np.logical_and(
                self.np_sensor_data[:, 2] >= start_timestamp,
                self.np_sensor_data[:, 2] <= end_timestamp,
            )
        ]
        distance_results = sensor_data_during_line[:, 3]

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
    start_time = time()
    logger.info("recompute() started")
    # remove previous results
    delete_edge_results(mysql_config, process_id)
    arc.delete_measured_arc_info(mysql_config, process_id)
    pair.delete_measured_length(mysql_config, process_id)
    delete_trace_line_results(mysql_config, process_id)
    update_mtct_latency(mysql_config, process_id, None)
    logger.info("delete previous results")

    process_data = status.get_process_status(mysql_config, process_id)
    model_id = process_data[1]
    result = Result(mysql_config, model_id, process_id)
    compute_start_time = time()
    edge_update_list, trace_line_update_list = result.compute_updating_data()
    logger.info(f"compute_updating_data() took {time() - compute_start_time} seconds")
    logger.info("compute_updating_data() done")

    edge_count = len(edge_update_list)
    if edge_count == 0:
        status.update_process_status(
            mysql_config,
            process_id,
            "Error at update_data_after_measurement()",
            "No edge found",
        )
        logger.warning("No edge found")
        return
    import_edge_results(edge_update_list, mysql_config)
    logger.info("import_edge_results() done")
    if trace_line_update_list:
        import_trace_line_results(mysql_config, trace_line_update_list)

    _msg = f"{edge_count} edges found"
    logger.info(_msg)

    try:
        pair.add_line_length(model_id, mysql_config, process_id)
        arc.add_measured_arc_info(model_id, mysql_config, process_id)
        status.update_process_status(mysql_config, process_id, "done")
        logger.info("done")
        logger.info(f"recompute() took {time() - start_time} seconds")
    except Exception as e:
        logger.warning(e)
        status.update_process_status(
            mysql_config, process_id, "Error at update_data_after_measurement()", str(e)
        )
