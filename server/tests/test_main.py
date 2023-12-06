from fastapi.testclient import TestClient
from server.main import app
import pytest

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_upload_3dmodel_only_lines():
    path = "tests/fixtures/stl/demo.STL"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 1}


def test_upload_3dmodel_with_arcs():
    path = "tests/fixtures/stl/sample.stl"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 2}


def test_upload_duplicate_3dmodel_only_lines():
    path = "tests/fixtures/stl/demo.STL"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 3}


def test_upload_duplicate_3dmodel_with_arcs():
    path = "tests/fixtures/stl/sample.stl"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 4}


def test_setup_data_only_lines():
    job_info = {
        "three_d_model_id": 3,
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_setup_data_only_lines_again():
    job_info = {
        "three_d_model_id": 3,
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_setup_data_wtih_arcs():
    job_info = {
        "three_d_model_id": 4,
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_setup_data_with_arcs_again():
    job_info = {
        "three_d_model_id": 4,
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_setup_data_with_arcs_with_offset():
    job_info = {
        "three_d_model_id": 4,
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 50.0,
        "y_offset": -65.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_with_new_model_with_step():
    path = "tests/fixtures/stl/step.STL"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 5}


def test_setup_data_with_step_and_slope():
    job_info = {
        "three_d_model_id": 5,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 1000.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.skip(reason="Not implemented")
def test_websocket():
    status = {
        "status": "off",
    }
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == status


def test_get_model_id_from_program_name():
    program_name = "1003"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": 3}

    program_name = "1004"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": 4}

    program_name = "34001 MIZO"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": None}

    program_name = "1005"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": 5}


def test_delete_model_data():
    path = "tests/fixtures/stl/test-Part.stl"
    model_id = 6

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": model_id}

    job_info = {
        "three_d_model_id": 6,
        "measure_length": 2.5,
        "measure_feedrate": 100.0,
        "move_feedrate": 1000.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
        "send_gcode": False,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.delete(f"/delete/model?model_id={model_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
