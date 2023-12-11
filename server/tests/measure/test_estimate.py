from server.measure.estimate import update_data_after_measurement, Result
from server.config import MYSQL_CONFIG
from server.listener import status
from fastapi.testclient import TestClient
from server.main import app
import pytest
from .mockdata import (
    create_mock_data,
    create_mock_missing_data,
    create_mock_multiple_edges,
    create_mock_perfect_data,
    create_mock_missing_mtconnect_data,
)

client = TestClient(app)
z = 10.0


@pytest.mark.skip(reason="Only for local testing")
def test_get_expected_z_value():
    result = Result(MYSQL_CONFIG, 3, 2)
    z = result.get_expected_z_value((0, 0))
    assert z == 0.0


@pytest.mark.skip(reason="Only for local testing")
def test_validate_sensor_output():
    result = Result(MYSQL_CONFIG, 1, 2)
    assert result.validate_sensor_output(9400, (-2.5, 0), (2.5, 0))
    assert not result.validate_sensor_output(18900, (-20.5, 0), (2.5, 0))


def test_update_data_after_measurement():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_missing_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc_missing_data():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_multiple_edges():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_with_arc_multiple_edges():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_different_gcode_params():
    job_info = {
        "three_d_model_id": 3,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 2000.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_different_gcode_params_with_arc():
    job_info = {
        "three_d_model_id": 4,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 2000.0,
        "x_offset": 50.0,
        "y_offset": -65.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_multiple_edges(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_perfect_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_perfect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/lines?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    lines = response.json()["lines"]
    for [_id, length, estimated_length] in lines:
        assert abs(length - estimated_length) < 0.005

    response = client.get(f"/result/arcs?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    arcs = response.json()["arcs"]
    for arc in arcs:
        radius = arc[1]
        estimated_radius = arc[5]
        assert abs(radius - estimated_radius) < 0.005


def test_update_data_after_measurement_perfect_data_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_perfect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/lines?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    lines = response.json()["lines"]
    for [_id, length, estimated_length] in lines:
        assert abs(length - estimated_length) < 0.005

    response = client.get(f"/result/arcs?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    arcs = response.json()["arcs"]
    for arc in arcs:
        radius = arc[1]
        if radius != 9:
            continue
        estimated_radius = arc[5]
        assert abs(radius - estimated_radius) < 0.01


def test_update_data_after_measurement_missing_mtconnect_data():
    filename = "demo.STL"
    model_id = 3
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_mtconnect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_missing_mtconnect_data_with_arc():
    filename = "sample.stl"
    model_id = 4
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_missing_mtconnect_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"


def test_update_data_after_measurement_step():
    filename = "step.STL"
    model_id = 5
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/steps?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    steps = response.json()["steps"]
    height = steps[0][1]
    estimated_height = steps[0][2]
    assert height == 3.0
    assert estimated_height == 3.0

    response = client.get(f"/result/slopes?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    slopes = response.json()["slopes"]
    angle = slopes[0][1]
    estimated_angle = slopes[0][2]
    assert angle == 45.0
    assert estimated_angle == 45.0


def test_update_data_after_measurement_step_fluctuating_data():
    filename = "step.STL"
    model_id = 5
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    create_mock_data(filename, process_id, fluctuation=0.1)
    update_data_after_measurement(MYSQL_CONFIG, process_id, model_id)
    process_result = status.get_process_status(MYSQL_CONFIG, process_id)
    assert process_result[2] == "done"

    response = client.get(f"/result/steps?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    steps = response.json()["steps"]
    height = steps[0][1]
    estimated_height = steps[0][2]
    assert height == 3.0
    print("estimated_height", estimated_height)

    response = client.get(f"/result/slopes?model_id={model_id}&process_id={process_id}")
    assert response.status_code == 200
    slopes = response.json()["slopes"]
    angle = slopes[0][1]
    estimated_angle = slopes[0][2]
    assert angle == 45.0
    print("estimated_angle", estimated_angle)


def test_delete_model_after_measurement():
    model_id = 3
    response = client.delete(f"/delete/model?model_id={model_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_delete_model_after_measurement_with_arc():
    model_id = 4
    response = client.delete(f"/delete/model?model_id={model_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_delete_model_after_measurement_with_step_slope():
    model_id = 5
    response = client.delete(f"/delete/model?model_id={model_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
