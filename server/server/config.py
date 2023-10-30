import os

# For github actions
CI_MYSQL_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
)


MYSQL_CONFIG = dict(
    host="192.168.122.76",
    port=3306,
    user="root",
    password="root",
)

if os.environ.get("CI"):
    MYSQL_CONFIG = CI_MYSQL_CONFIG


MODEL_PATH = "data/3dmodel"
GCODE_PATH = "data/gcode"

SENSOR_HOSTNAME = "opencmm"
SENSOR_IP = f"{SENSOR_HOSTNAME}.local"
