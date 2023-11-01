import json
from ping3 import ping


def send_config(interval: int, threshold: int):
    """
    Starts the streaming process
    """

    return json.dumps(
        {"command": "config", "interval": interval, "threshold": threshold}
    )


def deep_sleep():
    return json.dumps({"command": "deepSleep"})


def ping_sensor(sensor_ip: str):
    """
    Pings the sensor
    """
    return ping(sensor_ip)
