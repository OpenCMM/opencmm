from fastapi.testclient import TestClient
from server.config import get_config
from server.main import app
import pytest

client = TestClient(app)


def test_load():
    conf = get_config()
    sample_size = conf["edge"]["arc"]["number"]
    assert sample_size == 4
    mtct_disable = conf["mtconnect"]["disable"]
    assert mtct_disable is True


@pytest.mark.skip(reason="not implemented")
def test_mtconnect():
    response = client.get("/mtconnect_url")
    assert response.status_code == 200
    url = (
        "https://demo.metalogi.io/current?"
        "path=//Axes/Components/Linear/DataItems/DataItem"
    )
    assert response.json() == {"url": url}


@pytest.mark.skip(reason="not implemented")
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
