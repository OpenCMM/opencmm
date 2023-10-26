from fastapi.testclient import TestClient
from server.main import app


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
        assert response.json() == {"status": "ok"}


def test_setup_data():
    job_info = {
        "measure_length": 2.5,
        "measure_feedrate": 300.0,
        "move_feedrate": 600.0,
        "x_offset": 0.0,
        "y_offset": 0.0,
        "z_offset": 0.0,
    }
    response = client.post("/setup/data", json=job_info)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
