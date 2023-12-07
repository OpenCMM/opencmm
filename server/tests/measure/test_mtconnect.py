from server.measure.mtconnect import check_if_mtconnect_data_is_missing
from server.config import MYSQL_CONFIG
import pytest


@pytest.mark.skip(reason="Only for local testing")
def test_check_if_mtconnect_data_is_missing():
    check_if_mtconnect_data_is_missing(MYSQL_CONFIG, 4, 20)
