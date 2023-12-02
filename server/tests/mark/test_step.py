from server.mark.step import import_steps, create_step_path
from server.config import MYSQL_CONFIG
import pytest


@pytest.mark.skip(reason="Only for local testing")
def test_import_steps():
    import_steps(MYSQL_CONFIG, 22)
    assert 1 == 1


def test_create_step_path():
    model_id = 5
    path, trace_lines = create_step_path(MYSQL_CONFIG, model_id, "step.STL", 1000)
    assert path == [
        "G1 X12.5 Y-2.5 F1000",
        "G1 X12.5 Y-37.5 F300",
        "G1 X7.5 Y-2.5 F1000",
        "G1 X7.5 Y-37.5 F300",
    ]
    assert trace_lines == [
        [1, 12.5, -2.5, 12.5, -37.5, 0.0],
        [1, 7.5, -2.5, 7.5, -37.5, -3.0],
    ]
