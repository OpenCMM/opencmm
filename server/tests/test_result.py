from server.result import fetch_edge_result_combined
import pytest


@pytest.mark.skip(reason="Only for local testing")
def test_fetch_edge_result_combined():
    fetch_edge_result_combined(4, 20)
