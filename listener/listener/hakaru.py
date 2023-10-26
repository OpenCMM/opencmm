import json


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
