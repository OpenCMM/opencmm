from server.measure.mtconnect import check_if_mtconnect_data_is_missing, MtctDataChecker
from server.config import MYSQL_CONFIG
import pytest
import numpy as np


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
