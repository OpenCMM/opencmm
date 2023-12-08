import mysql.connector
from server.model import get_model_data
from server.mark.gcode import get_gcode_filename
from server.config import GCODE_PATH, get_config
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
import numpy as np


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
        gcode_filename = get_gcode_filename(filename)
        gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
        self.gcode = load_gcode(gcode_file_path)
        mtconnect_data = get_mtconnect_data(self.process_id, self.mysql_config)
        self.np_mtconnect_data = np.array(mtconnect_data)
        self.trace_ids = get_trace_ids(self.mysql_config, self.model_id)
        self.last_line = len(self.gcode) + 2
        if self.trace_ids:
            self.last_line -= 1
        self.init_line = 4
        self.lines = []
        self.first_line_for_tracing = get_first_line_number_for_tracing(
            self.mysql_config, self.model_id
        )
        self.config = get_config()

    def add_missing_timestamps(self, lines):
        """
        Add missing timestamps to lines
        """
        new_lines = []
        current_line = lines[0][0]
        for i in range(len(lines)):
            assert lines[i][0] >= current_line

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

    def estimate_timestamps_from_mtct_data(self, mtconnect_latency: float = None):
        lines = []
        mtconnect_latency = mtconnect_latency or self.config["mtconnect"]["latency"]

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

        missing_lines_added = self.add_missing_timestamps(lines)
        return np.array(missing_lines_added)
