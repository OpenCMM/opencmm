import pytest
from server.listener.hakaru import (
    ping_sensor,
)


@pytest.mark.skip(reason="No MQTT broker running")
def test_ping_sensor():
    assert ping_sensor() is True
