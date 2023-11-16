from fastapi.testclient import TestClient
from server.config import get_config
from server.main import app

client = TestClient(app)


def test_load():
    sample_size = get_config()["edge"]["arc"]["number"]
    assert sample_size == 4


def test_mtconnect():
    response = client.get("/mtconnect_url")
    assert response.status_code == 200
    url = (
        "https://demo.metalogi.io/current?"
        "path=//Axes/Components/Linear/DataItems/DataItem"
    )
    assert response.json() == {"url": url}


def test_update_mtconnect():
    new_url = "https://demo.metalogi.io/current"
    response = client.get("/mtconnect_url")
    assert response.status_code == 200
    current_url = response.json()["url"]

    response = client.post(f"/update/mtconnect_url?url={new_url}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    response = client.get("/mtconnect_url")
    assert response.status_code == 200
    assert response.json() == {"url": new_url}

    response = client.post(f"/update/mtconnect_url?url={current_url}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
