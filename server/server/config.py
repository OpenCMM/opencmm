import os

# For github actions
CI_MYSQL_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
)

MYSQL_URL = os.getenv("MYSQL_URL", "192.168.122.230")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

MYSQL_CONFIG = dict(
    host=MYSQL_URL,
    port=MYSQL_PORT,
    user="root",
    password="root",
)

if os.environ.get("CI"):
    MYSQL_CONFIG = CI_MYSQL_CONFIG

MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "192.168.10.104")

MODEL_PATH = "data/3dmodel"
GCODE_PATH = "data/gcode"

SENSOR_HOSTNAME = "opencmm"
SENSOR_IP = f"{SENSOR_HOSTNAME}.local"
