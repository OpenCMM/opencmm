from fastapi.testclient import TestClient
from server.main import app
import pytest

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_upload_3dmodel():
    path = "tests/fixtures/stl/sample.stl"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 1}


def test_upload_duplicate_3dmodel():
    path = "tests/fixtures/stl/sample.stl"

    with open(path, "rb") as f:
        response = client.post("/upload/3dmodel", files={"file": f})
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "model_id": 1}


# @pytest.mark.skip(reason="Cannot test without windows machine")
def test_setup_data():
    job_info = {
        "three_d_model_id": 1,
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


# @pytest.mark.skip(reason="Cannot test without windows machine")
def test_setup_data_with_duplicate_model_id():
    job_info = {
        "three_d_model_id": 1,
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


@pytest.mark.skip(reason="Not implemented")
def test_websocket():
    status = {
        "status": "off",
    }
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == status


def test_get_model_id_from_program_name():
    program_name = "1001"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": 1}

    program_name = "34001 MIZO"
    response = client.get(f"/get_model_id/from/program_name/{program_name}")
    assert response.status_code == 200
    assert response.json() == {"model_id": None}
