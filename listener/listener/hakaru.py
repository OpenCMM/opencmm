import json
from ping3 import ping


def start_streaming(interval: int, threshold: int):
    """
    Starts the streaming process
    """

    return json.dumps(
        {"command": "start", "interval": interval, "threshold": threshold}
    )


def stop_streaming():
    """
    Stops the streaming process
    """

    return json.dumps({"command": "stop", "interval": 1000, "threshold": 100})


def deep_sleep():
    return json.dumps({"command": "deepSleep", "interval": 1000, "threshold": 100})


def ping_sensor(sensor_ip: str):
    """
    Pings the sensor
    """
    return ping(sensor_ip)
