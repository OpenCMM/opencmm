import mysql.connector
from server.config import get_config


def get_sensor_data(process_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM sensor WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows


def sensor_output_diff_to_mm(sensor_output_diff: float):
    """
    Convert sensor output difference to mm
    """
    conf = get_config()
    sensor_middle_output = conf["sensor"]["middle_output"]
    # sensor_middle_output = 0.0mm
    # sensor_middle_output - 798 = -3.02mm
    # when sensor_middle_output = 9400
    return (3.02 * sensor_output_diff / 798) * (9400 / sensor_middle_output)


def sensor_output_to_mm(sensor_output: float):
    """
    Convert raw sensor output to mm \n
    The distance between sensor and model is 100.0mm when this value is 0.0mm
    """
    conf = get_config()
    sensor_middle_output = conf["sensor"]["middle_output"]
    return sensor_output_diff_to_mm(sensor_output - sensor_middle_output)
