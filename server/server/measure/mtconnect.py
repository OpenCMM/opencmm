import mysql.connector
from server.model import get_model_data
from server.mark.gcode import get_gcode_filename
from server.listener import status
from server.config import GCODE_PATH, MODEL_PATH, get_config
import trimesh
from .sensor import get_sensor_data, sensor_output_to_mm
from server.measure.gcode import (
    load_gcode,
    get_true_line_number,
    get_true_line_and_feedrate,
    row_to_xyz_feedrate,
    get_start_end_points_from_line_number,
    get_timestamp_at_point,
)
from datetime import timedelta
from server.mark.trace import get_first_line_number_for_tracing
from server.mark.trace import get_trace_ids
from server.prepare import create_gcode_path
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def get_mtconnect_data(process_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM mtconnect WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows


def check_if_mtconnect_data_is_missing(
    mysql_config: dict, model_id: int, process_id: int
):
    """
    Check if mtconnect data is missing and return missing data
    """
    model_row = get_model_data(model_id)
    filename = model_row[1]
    gcode_filename = get_gcode_filename(filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode = load_gcode(gcode_file_path)
    mtconnect_data = get_mtconnect_data(process_id, mysql_config)
    np_mtconnect_data = np.array(mtconnect_data)

    trace_ids = get_trace_ids(mysql_config, model_id)
    last_line = len(gcode) + 2
    if trace_ids:
        last_line -= 1
    # if data is not missing, line 4 ~ last_line should be in np_mtconnect_data
    # odd line numbers are okay to be missing
    init_line = 4
    lines = []

    first_line_for_tracing = get_first_line_number_for_tracing(mysql_config, model_id)
    for row in np_mtconnect_data:
        xy = (row[3], row[4])
        line = int(row[6])
        line = get_true_line_number(xy, line, gcode, first_line_for_tracing)
        if line:
            lines.append(line)
    unique_lines = np.unique(lines)

    missing_lines = []
    for line in range(init_line, last_line + 2, 2):
        if line not in unique_lines:
            (start, end, feedrate) = get_start_end_points_from_line_number(gcode, line)
            data = {
                "id": line,
                "start": start,
                "end": end,
                "feedrate": round(feedrate, 3),
            }
            missing_lines.append(data)

    return missing_lines


class MtctDataChecker:
    def __init__(self, mysql_config: dict, model_id: int, process_id: int):
        self.mysql_config = mysql_config
        self.model_id = model_id
        self.process_id = process_id
        self.model_row = get_model_data(model_id)
        filename = self.model_row[1]
        self.stl_filepath = f"{MODEL_PATH}/{filename}"
        self.mesh = trimesh.load(self.stl_filepath)
        process_status = status.get_process_status(mysql_config, process_id)
        self.offset = (process_status[4], process_status[5], process_status[6])
        self.load_gcode()
        mtconnect_data = get_mtconnect_data(self.process_id, self.mysql_config)
        self.np_mtconnect_data = np.array(mtconnect_data)
        self.last_line = len(self.gcode) + 2
        self.init_line = 4
        self.lines = []
        self.first_line_for_tracing = get_first_line_number_for_tracing(
            self.mysql_config, self.model_id
        )
        self.config = get_config()
        self.set_mtct_latency()

    def load_gcode(self):
        current_gcode_settings = self.get_current_gcode_settings()
        gcode_settings = self.get_gcode_settings()
        stl_filename = self.model_row[1]
        if current_gcode_settings == gcode_settings:
            gcode_filename = get_gcode_filename(stl_filename)
            gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
            self.gcode = load_gcode(gcode_file_path)
        else:
            offset = (self.model_row[3], self.model_row[4], self.model_row[5])
            gcode_with_str = create_gcode_path(
                self.mysql_config,
                self.model_id,
                stl_filename,
                gcode_settings,
                offset,
                False,
            )
            self.gcode = [row.split() for row in gcode_with_str]

    def get_current_gcode_settings(self):
        """
        Get gcode settings from the process
        """
        cnx = mysql.connector.connect(**self.mysql_config, database="coord")
        cursor = cnx.cursor()
        query = (
            "SELECT measurement_range, measure_feedrate, move_feedrate "
            "FROM model WHERE id = %s"
        )
        cursor.execute(query, (self.model_id,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        return row

    def get_gcode_settings(self):
        """
        Get gcode settings from the process
        """
        cnx = mysql.connector.connect(**self.mysql_config, database="coord")
        cursor = cnx.cursor()
        query = (
            "SELECT measurement_range, measure_feedrate, move_feedrate "
            "FROM process WHERE id = %s"
        )
        cursor.execute(query, (self.process_id,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        return row

    def find_idx_of_first_line_number(self, lines):
        if lines[0][0] != self.last_line:
            return 0
        current_line = lines[0][0]
        for i, line in enumerate(lines):
            if line[0] < current_line:
                return i
            current_line = line[0]

    def remove_falsely_added_last_lines(self, lines):
        return lines[self.find_idx_of_first_line_number(lines) :]

    def add_missing_timestamps(self, lines):
        """
        Add missing timestamps to lines
        """
        new_lines = []
        current_line = lines[0][0]
        for i in range(len(lines)):
            if lines[i][0] < current_line:
                # line should be in order
                continue

            line_number = lines[i][0]
            if line_number == current_line:
                new_lines.append(lines[i])
                continue

            if line_number == current_line + 2:
                # i-1 is missing
                # add i-1
                new_lines.append([current_line + 1, lines[i - 1][2], lines[i][1]])

            new_lines.append(lines[i])
            current_line = line_number
        return new_lines

    def get_missing_lines(self, lines):
        missing_lines = []
        current_line = lines[0][0]
        for i in range(len(lines)):
            if lines[i][0] < current_line:
                # line should be in order
                continue

            line_number = lines[i][0]

            if line_number == current_line + 2:
                # i-1 is missing
                # add i-1
                (start, end, feedrate) = get_start_end_points_from_line_number(
                    self.gcode, current_line + 1
                )
                missing_lines.append(
                    [
                        current_line + 1,
                        lines[i - 1][2],
                        lines[i][1],
                        *start,
                        *end,
                        feedrate,
                    ]
                )

            current_line = line_number
        return missing_lines

    def to_line_row(self, line_candidate, xy, timestamp):
        feedrate = line_candidate[1]
        start = line_candidate[2]
        end = line_candidate[3]
        start_timestamp = get_timestamp_at_point(xy, start, feedrate, timestamp, True)
        end_timestamp = get_timestamp_at_point(xy, end, feedrate, timestamp, False)
        return [line_candidate[0], start_timestamp, end_timestamp]

    def get_travel_time(self, start, end, feedrate_per_min):
        travel_time_in_sec = (
            np.linalg.norm(np.array(start) - np.array(end)) / feedrate_per_min * 60
        )
        return timedelta(seconds=travel_time_in_sec)

    def estimate_line_numbers_from_previous_line(self, previous_line, timestamp):
        """
        Estimate line numbers from the previous line
        """
        if previous_line[2] > timestamp:
            # timestamp is before the previous line ends
            return previous_line[0]

        end_timestamp = previous_line[2]
        gcode_after_line_number = self.gcode_after_line_number(previous_line[0])
        previous_line_gcode_row = row_to_xyz_feedrate(gcode_after_line_number[0])
        start = (previous_line_gcode_row[0], previous_line_gcode_row[1])
        for i in range(1, len(gcode_after_line_number)):
            row = row_to_xyz_feedrate(gcode_after_line_number[i])
            end = (row[0], row[1])
            end_timestamp += self.get_travel_time(start, end, row[2])
            if end_timestamp > timestamp:
                return previous_line[0] + i
            start = end

    def gcode_after_line_number(self, line_number):
        assert line_number >= 3
        return self.gcode[line_number - 3 :]

    def add_start_end_coordinates(self, lines):
        """
        Add start and end coordinates to lines
        """
        new_lines = []
        for line in lines:
            line_number = line[0]
            (start, end, feedrate) = get_start_end_points_from_line_number(
                self.gcode, line_number
            )
            new_lines.append([*line, *start, *end, feedrate])
        return new_lines

    def remove_duplicate_lines(self, lines):
        """
        Remove duplicate lines
        """
        new_lines = []
        current_line = lines[0]
        for line in lines[1:]:
            if line[0] == current_line[0]:
                continue
            new_lines.append(current_line)
            current_line = line
        new_lines.append(current_line)
        return new_lines

    def estimate_timestamps_from_mtct_data(
        self,
        mtconnect_latency: float = None,
        add_missing: bool = True,
        remove_duplicate: bool = True,
    ):
        lines = []
        mtconnect_latency = mtconnect_latency or self.mtct_latency

        for row in self.np_mtconnect_data:
            xy = (row[3], row[4])
            line = int(row[6])
            timestamp = row[2] - timedelta(milliseconds=mtconnect_latency)
            line_candidates = get_true_line_and_feedrate(
                xy, line, self.gcode, self.first_line_for_tracing
            )
            if not line_candidates:
                continue

            _line_rows = [
                self.to_line_row(line_candidate, xy, timestamp)
                for line_candidate in line_candidates
            ]
            if len(_line_rows) == 1:
                lines.append(_line_rows[0])
            else:
                # multiple lines are possible
                # estimate which line is more likely from the previous line
                previous_line = lines[-1]
                estimated_line = self.estimate_line_numbers_from_previous_line(
                    previous_line, timestamp
                )
                if not estimated_line:
                    continue
                for _line_row in _line_rows:
                    if _line_row[0] == estimated_line:
                        lines.append(_line_row)
                        break

        lines = self.remove_falsely_added_last_lines(lines)
        if add_missing:
            lines = self.add_missing_timestamps(lines)
        lines_with_coordinates = self.add_start_end_coordinates(lines)
        if remove_duplicate:
            lines_with_coordinates = self.remove_duplicate_lines(lines_with_coordinates)
        return np.array(lines_with_coordinates)

    def adjust_delays(self, lines):
        """
        Change timestamps with delays deviated from the average
        """
        avg, delays = self.get_average_delay_between_lines()
        # get deviated delays
        deviated_delays = []
        for delay in delays:
            if delay[2] > avg * 2:
                deviated_delays.append(delay)
        for line in lines:
            for deviated_delay in deviated_delays:
                # switch deviated delay to the average
                if line[0] == deviated_delay[1]:
                    line[1] -= timedelta(seconds=deviated_delay[2] - avg)
                    line[2] -= timedelta(seconds=deviated_delay[2] - avg)
                    break
        return lines

    def get_delay(self, lines):
        prev_line_end = lines[0][2]
        prev_line_number = lines[0][0]
        delays = []
        for i in range(1, len(lines)):
            line = lines[i]
            line_number = line[0]
            if line_number - 1 == prev_line_number:
                delay = line[1] - prev_line_end
                delays.append([prev_line_number, line_number, delay.total_seconds()])

            prev_line_number = line_number
            prev_line_end = line[2]

        return delays

    def robust_mean(self, data):
        """
        Calculates the robust mean of a 1D numpy array
        by filtering out significantly deviated elements.

        Args:
            data: A 1D numpy array.

        Returns:
            The robust mean of the data.
        """
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        filtered_data = data[np.abs(data - median) <= 3 * mad]
        return np.mean(filtered_data)

    def get_average_delay_between_lines(self):
        """
        Get average delay between lines, which is the time
        took to move from one line to another
        """
        lines = self.estimate_timestamps_from_mtct_data(
            add_missing=False, remove_duplicate=True
        )
        delays = self.get_delay(lines)
        if not delays:
            return 0, []
        delays = np.array(delays)
        return self.robust_mean(delays[:, 2]), delays

    def missing_line_travel_time_diff(self):
        lines = self.estimate_timestamps_from_mtct_data(
            add_missing=False, remove_duplicate=True
        )
        missing_lines = self.get_missing_lines(lines)
        diff_list = []
        for line in missing_lines:
            line_number = line[0]
            start = line[3:5]
            end = line[5:7]
            if start == end:
                continue
            travel_time = self.get_travel_time(start, end, line[7] * 60)
            actual_time = line[2] - line[1]
            diff = actual_time - travel_time
            diff_list.append([line_number, diff.total_seconds()])

        if not diff_list:
            return None, None
        np_diff = np.array(diff_list)
        avg_diff = self.robust_mean(np_diff[:, 1])
        return avg_diff, np_diff

    def get_mtct_latency_from_process(self):
        """
        Get mtconnect latency from process
        """
        cnx = mysql.connector.connect(**self.mysql_config, database="coord")
        cursor = cnx.cursor()
        query = "SELECT mtct_latency FROM process WHERE id = %s"
        cursor.execute(query, (self.process_id,))
        row = cursor.fetchone()
        if not row:
            return None
        cursor.close()
        cnx.close()
        return row[0]

    def get_direction_vector(self, start, end):
        direction_vector = np.array([end[0] - start[0], end[1] - start[1]])
        distance = np.linalg.norm(direction_vector)
        return direction_vector / distance

    def calc_coord_from_timestamp(self, lines, timestamp):
        """
        Calculate the coordinates from timestamp
        """
        for line in lines:
            start_timestamp = line[1]
            end_timestamp = line[2]
            if start_timestamp <= timestamp <= end_timestamp:
                start = (line[3], line[4])
                end = (line[5], line[6])
                if start == end:
                    continue

                direction_vector = self.get_direction_vector(start, end)
                feedrate = line[7]
                timestamp_diff = timestamp - start_timestamp
                distance = feedrate * timestamp_diff.total_seconds()
                coord = np.array(start) + distance * direction_vector
                # round to 3 decimal places
                coord = np.round(coord, 3)
                return tuple(coord)

    def sensor_timestamp_to_coord(
        self,
        start_timestamp: datetime,
        sensor_timestamp: datetime,
        start: tuple,
        end: tuple,
        feedrate: float,
    ):
        """
        Estimate the coordinate of the edge from sensor timestamp

        Args:
            start_timestamp: Start timestamp of the line
            sensor_timestamp: Sensor timestamp
            start: Start coordinate of the line
            end: End coordinate of the line
            feedrate: Feedrate of the line

        Returns:
            Estimated coordinate of the sensor at the given timestamp
        """
        beam_diameter = self.config["sensor"]["beam_diameter"]  # in μm
        sensor_response_time = self.config["sensor"]["response_time"]  # in ms
        direction_vector = self.get_direction_vector(start, end)
        # factor in sensor response time
        sensor_timestamp -= timedelta(milliseconds=sensor_response_time)
        timestamp_diff = sensor_timestamp - start_timestamp
        distance = feedrate * timestamp_diff.total_seconds()
        beam_diameter = beam_diameter / 1000  # convert to mm
        distance_with_beam_diameter = (
            distance + beam_diameter / 2
        )  # add half of beam radius
        coord = np.array(start) + distance_with_beam_diameter * direction_vector
        # round to 3 decimal places
        coord = np.round(coord, 3)
        return tuple(coord)

    def set_mtct_latency(self):
        """
        Set mtconnect latency
        """
        mtct_latency_from_process = self.get_mtct_latency_from_process()
        if mtct_latency_from_process:
            self.mtct_latency = self.get_mtct_latency_from_process()
            return
        # load the default mtct latency
        self.mtct_latency = self.config["mtconnect"]["latency"]
        # find the best mtct latency
        mtct_latency_range = (
            self.config["mtconnect"]["latency_start"],
            self.config["mtconnect"]["latency_end"],
        )
        step = self.config["mtconnect"]["latency_step"]
        mtct_latency, edge_count, avg_distance = self.find_mtct_latency(
            mtct_latency_range, step
        )

        if edge_count != 0:
            logger.info(
                (
                    f"mtct_latency: {mtct_latency} edge_count: {edge_count} "
                    f"avg_distance: {avg_distance}"
                )
            )
            self.mtct_latency = mtct_latency
            update_mtct_latency(self.mysql_config, self.process_id, mtct_latency)

    def get_sensor_data_with_coordinates(self, mtct_latency: float = None):
        """
        Get sensor data with coordinates
        """
        if mtct_latency is None:
            mtct_latency = self.mtct_latency

        lines = self.estimate_timestamps_from_mtct_data(mtct_latency)
        lines = self.adjust_delays(lines)
        sensor_data = get_sensor_data(self.process_id, self.mysql_config)
        sensor_data_with_coordinates = []
        for row in sensor_data:
            sensor_timestamp = row[2]
            sensor_output = row[3]
            for line in lines:
                start_timestamp = line[1]
                end_timestamp = line[2]
                if start_timestamp <= sensor_timestamp <= end_timestamp:
                    start = (line[3], line[4])
                    end = (line[5], line[6])
                    if start == end:
                        continue

                    feedrate = line[7]
                    sensor_coord = self.sensor_timestamp_to_coord(
                        start_timestamp,
                        sensor_timestamp,
                        start,
                        end,
                        feedrate,
                    )
                    line_number = line[0]
                    sensor_data_with_coordinates.append(
                        [line_number, *sensor_coord, sensor_timestamp, sensor_output]
                    )
                    break

        return sensor_data_with_coordinates, mtct_latency

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

    def validate_sensor_output_with_trimesh(
        self, sensor_output: float, start: tuple, end: tuple
    ):
        """
        Validate sensor output using trimesh ray intersection

        Args:
            sensor_output: Sensor output
            start: Start coordinate of the line
            end: End coordinate of the line

        Returns:
            True if the sensor output is valid, False otherwise
        """
        measured_z = sensor_output_to_mm(sensor_output)
        # measuring edge is the middle point of the line
        edge_xy = (np.array(start) + np.array(end)) / 2
        expected_z = self.get_expected_z_value(edge_xy)
        # sensor outputs >18800 when there is no workpiece in the sensor range
        if expected_z is None:
            return sensor_output > 18800
        if -35 <= expected_z <= 35:
            return abs(measured_z - expected_z) < self.config["sensor"]["tolerance"]
        return sensor_output > 18800

    def get_edge_coordinates_from_line_number(self, line_number: int):
        cnx = mysql.connector.connect(**self.mysql_config, database="coord")
        cursor = cnx.cursor()
        query = "SELECT id, x, y, z FROM edge WHERE line = %s " "AND model_id = %s"
        cursor.execute(query, (line_number, self.model_id))
        rows = cursor.fetchall()
        if not rows:
            return None
        cursor.close()
        cnx.close()
        return rows

    def validate_sensor_output(self, sensor_output: float, line_number: int):
        """
        Validate sensor output using edge table data

        Args:
            sensor_output: Sensor output
            line_number: Line number

        Returns:
            True if the sensor output is valid, False otherwise
            Edge ids
        """
        measured_z = sensor_output_to_mm(sensor_output)
        edges = self.get_edge_coordinates_from_line_number(line_number)
        if not edges:
            return False, None
        # expected_z is the highest z value of the edges
        expected_z = max([edge[3] for edge in edges]) + self.offset[2]

        edge_ids = [edge[0] for edge in edges]
        # sensor outputs >18800 when there is no workpiece in the sensor range
        if expected_z is None:
            return sensor_output > 18800, edge_ids
        if -35 <= expected_z <= 35:
            return (
                abs(measured_z - expected_z) < self.config["sensor"]["tolerance"],
                edge_ids,
            )
        return sensor_output > 18800, edge_ids

    def get_only_edge_detection_lines(self, lines):
        edge_detection_lines = []
        for line in lines:
            line_number = line[0]
            # Edge detection
            if (
                not self.first_line_for_tracing
                or line_number < self.first_line_for_tracing - 2
            ):
                if line_number % 2 != 0:
                    # Not measuring
                    continue
                edge_detection_lines.append(line)
        return edge_detection_lines

    def sensor_data_count_and_distance_when_measuring(self, mtct_latency: float):
        """
        Get sensor data count when measuring
        """
        count = 0
        distances = []
        lines = self.estimate_timestamps_from_mtct_data(mtct_latency)
        lines = self.adjust_delays(lines)
        edge_detection_lines = self.get_only_edge_detection_lines(lines)
        sensor_data = get_sensor_data(self.process_id, self.mysql_config)
        prev_line_number = None
        for row in sensor_data:
            sensor_timestamp = row[2]
            sensor_output = row[3]
            for line in edge_detection_lines:
                line_number = line[0]
                # One edge per line
                if line_number == prev_line_number:
                    continue
                start_timestamp = line[1]
                end_timestamp = line[2]
                if start_timestamp <= sensor_timestamp <= end_timestamp:
                    start = (line[3], line[4])
                    end = (line[5], line[6])
                    if start == end:
                        continue

                    sensor_output_valid, _ = self.validate_sensor_output(
                        sensor_output, line_number
                    )
                    if not sensor_output_valid:
                        continue

                    feedrate = line[7]
                    measured_edge_coord = self.sensor_timestamp_to_coord(
                        start_timestamp,
                        sensor_timestamp,
                        start,
                        end,
                        feedrate,
                    )
                    edge_coord = (np.array(start) + np.array(end)) / 2
                    distances.append(
                        np.linalg.norm(
                            np.array(measured_edge_coord) - np.array(edge_coord)
                        )
                    )
                    count += 1
                    prev_line_number = line_number
                    break

        if count == 0:
            return 0, 1000
        np_distances = np.array(distances)
        return count, np.mean(np_distances)

    def find_mtct_latency(self, latency_range: tuple, step: float):
        """
        Find mtconnect latency
        """
        count_and_avg_distance = []

        for i in range(int((latency_range[1] - latency_range[0]) / step)):
            _mtct_latency = latency_range[0] + i * step
            (
                sensor_data_count,
                avg_distance,
            ) = self.sensor_data_count_and_distance_when_measuring(_mtct_latency)
            count_and_avg_distance.append(
                [_mtct_latency, sensor_data_count, avg_distance]
            )

        count_and_avg_distance.sort(key=lambda x: (-x[1], x[2]))
        return count_and_avg_distance[0]


def update_mtct_latency(mysql_config: dict, process_id: int, mtct_latency: float):
    """
    Update mtconnect latency of the process
    """
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "UPDATE process SET mtct_latency = %s WHERE id = %s"
    cursor.execute(query, (mtct_latency, process_id))
    cnx.commit()
    cursor.close()
    cnx.close()
