from server.measure.mtconnect import (
    check_if_mtconnect_data_is_missing,
    MtctDataChecker,
    update_mtct_latency,
)
from server.config import MYSQL_CONFIG, get_config
import pytest
import numpy as np
from datetime import datetime, timedelta
import csv


def test_update_mtct_latency():
    update_mtct_latency(MYSQL_CONFIG, 1, None)


@pytest.mark.skip(reason="Only for local testing")
def test_find_mtct_latency():
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, 2, 4)
    mtct_latency_range = (2800, 3200)
    step = 20
    mtct_latency, edge_count, avg_distance = mtct_data_checker.find_mtct_latency(
        mtct_latency_range, step
    )
    print(mtct_latency, edge_count, avg_distance)


@pytest.mark.skip(reason="Only for local testing")
def test_check_if_mtconnect_data_is_missing():
    check_if_mtconnect_data_is_missing(MYSQL_CONFIG, 4, 20)


@pytest.mark.skip(reason="Only for local testing")
def test_check_if_mtconnect_data_is_missing_debug():
    check_if_mtconnect_data_is_missing(MYSQL_CONFIG, 1, 1)


@pytest.mark.skip(reason="Only for local testing")
def test_estimate_timestamps_from_mtct_data():
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, 1, 1)

    lines = mtct_data_checker.estimate_timestamps_from_mtct_data()
    line_numbers = lines[:, 0]
    unique_lines = np.unique(line_numbers)
    # should be 4, 5, 6,,,, 74
    assert unique_lines[0] == 4
    assert unique_lines[-1] == 74
    assert len(unique_lines) == 71
    # Assuming line_numbers is the numpy array you want to check
    expected_line_numbers = np.arange(4, 75)

    # Check if line_numbers contains the expected sequence
    is_sequence_correct = np.array_equal(unique_lines, expected_line_numbers)
    assert is_sequence_correct


def sensor_timestamp_to_coord(
    start_timestamp: datetime,
    sensor_timestamp: datetime,
    xy: tuple,
    direction_vector: tuple,
    feedrate: float,
):
    """
    Estimate the coordinate of the edge from sensor timestamp
    """
    conf = get_config()
    beam_diameter = conf["sensor"]["beam_diameter"]  # in μm
    sensor_response_time = conf["sensor"]["response_time"]  # in ms
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


@pytest.mark.skip(reason="Only for local testing")
def test_estimate_timestamps_from_mtct_data_and_save():
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, 2, 4)
    lines = mtct_data_checker.estimate_timestamps_from_mtct_data()

    coordinate_data = []
    process_start = lines[0][1]
    process_end = lines[-1][2]
    time_took = process_end - process_start
    interval = 250.0
    data_count = int(time_took.total_seconds() / (interval / 1000))

    current_line = 0
    current_coord = None
    for i in range(data_count):
        timestamp = process_start + timedelta(milliseconds=i * interval)

        while current_line < len(lines):
            line = lines[current_line]
            if line[1] <= timestamp <= line[2]:
                start = (line[3], line[4])
                end = (line[5], line[6])
                if start == end:
                    coordinate_data.append([line[0], *current_coord, timestamp])
                    break
                direction_vector = np.array([end[0] - start[0], end[1] - start[1]])
                distance = np.linalg.norm(direction_vector)
                direction_vector = tuple(direction_vector / distance)
                sensor_coord = sensor_timestamp_to_coord(
                    line[1],
                    timestamp,
                    start,
                    direction_vector,
                    line[7],
                )
                current_coord = sensor_coord
                coordinate_data.append([line[0], *sensor_coord, timestamp])
                break
            else:
                current_line += 1
                continue

    print(f"len(coordinate_data): {len(coordinate_data)}")

    # save as csv
    with open("tests/coordinate_data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["line_number", "x", "y", "z", "timestamp"])
        for row in coordinate_data:
            writer.writerow(row)


@pytest.mark.skip(reason="Only for local testing")
def test_get_average_delay_between_lines():
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, 2, 4)
    avg_delay = mtct_data_checker.get_average_delay_between_lines()
    assert avg_delay < 0.002
    assert avg_delay > 0.001


@pytest.mark.skip(reason="Only for local testing")
def test_check_missing_lines():
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, 2, 4)
    avg_diff = mtct_data_checker.missing_line_travel_time_diff()
    assert avg_diff < 0.005
