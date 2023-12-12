import os
import yaml

# For github actions
CI_MYSQL_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
)

# MYSQL_URL = os.getenv("MYSQL_URL", "192.168.0.19")
MYSQL_URL = os.getenv("MYSQL_URL", "192.168.122.76")
# MYSQL_URL = os.getenv("MYSQL_URL", "yuchi-ubuntu.local")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
# MYSQL_PORT = os.getenv("MYSQL_PORT", "3307")

MYSQL_CONFIG = dict(
    host=MYSQL_URL,
    port=MYSQL_PORT,
    user="root",
    password="root",
)

# MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "192.168.0.19")
MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "192.168.122.76")
# MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "yuchi-ubuntu.local")
CI_MQTT_BROKER_URL = "localhost"

if os.environ.get("CI"):
    MYSQL_CONFIG = CI_MYSQL_CONFIG
    MQTT_BROKER_URL = CI_MQTT_BROKER_URL

MODEL_PATH = "data/3dmodel"
GCODE_PATH = "data/gcode"

SENSOR_HOSTNAME = "opencmm"
SENSOR_IP = f"{SENSOR_HOSTNAME}.local"


CONTROL_SENSOR_TOPIC = "sensor/control"
RECEIVE_DATA_TOPIC = "sensor/data"
PING_TOPIC = "sensor/ping"
PONG_TOPIC = "sensor/pong"
PROCESS_CONTROL_TOPIC = "process/control"
LISTENER_LOG_TOPIC = "log/listener"
IMPORT_SENSOR_TOPIC = "import/sensor"
IMPORT_MTCONNECT_TOPIC = "import/mtconnect"


MQTT_USERNAME = "opencmm"
MQTT_PASSWORD = "opencmm"

CONFIG_PATH = "data/config/dev.yaml"


def get_config():
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def update_conf(config: dict):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)
