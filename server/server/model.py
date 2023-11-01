from server.config import MODEL_PATH, MYSQL_CONFIG
import os
import mysql.connector


def add_new_3dmodel(filename: str) -> int:
    if not model_exists(filename):
        cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
        cursor = cnx.cursor()
        query = "INSERT INTO model (filename) VALUES (%s)"
        cursor.execute(query, (filename,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return cursor.lastrowid
    else:
        return filename_to_model_id(filename)


def list_3dmodel():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id, filename FROM model"
    cursor.execute(query)
    models_data = []
    for model in cursor:
        model_id = model[0]
        filename = model[1]
        model_path = os.path.join(MODEL_PATH, filename)
        model_size = os.path.getsize(model_path)
        model_modified_time = int(os.path.getmtime(model_path) * 1000)
        models_data.append(
            {
                "model_id": model_id,
                "name": filename,
                "size": model_size,
                "modified_time": model_modified_time,
            }
        )
    return models_data


def get_3dmodel_data():
    """
    Get 3d model data on the model path.

    Data includes file name, file size, last modified time, and gcode status.
    """

    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id, filename FROM model"
    cursor.execute(query)
    models_data = []
    for model in cursor:
        model_id = model[0]
        filename = model[1]
        model_path = os.path.join(MODEL_PATH, filename)
        model_size = os.path.getsize(model_path)
        model_modified_time = int(os.path.getmtime(model_path) * 1000)
        gcode_ready = os.path.exists(f"data/gcode/{filename}.gcode")
        sensor_status = get_sensor_status(model_id)
        model_status = get_model_status(gcode_ready, sensor_status)
        models_data.append(
            {
                "id": model_id,
                "name": filename,
                "size": model_size,
                "modified_time": model_modified_time,
                "gcode_ready": gcode_ready,
                "model_status": model_status,
            }
        )
    return models_data


def get_recent_3dmodel_data(limit: int):
    models = list_3dmodel()
    recent_models = sorted(models, key=lambda x: x["modified_time"], reverse=True)
    return recent_models[:limit]


def get_3dmodel_file_info(model_id: int):
    filename = model_id_to_filename(model_id)
    gcode_ready = os.path.exists(f"data/gcode/{filename}.gcode")
    sensor_status = get_sensor_status(model_id)
    model_status = get_model_status(gcode_ready, sensor_status)
    return {
        "id": model_id,
        "name": filename,
        "size": os.path.getsize(os.path.join(MODEL_PATH, filename)),
        "modified_time": int(
            os.path.getmtime(os.path.join(MODEL_PATH, filename)) * 1000
        ),
        "gcode_ready": gcode_ready,
        "model_status": model_status,
    }


def get_model_status(gcode_ready, sensor_status):
    if gcode_ready and sensor_status == "done":
        return 3
    elif gcode_ready and sensor_status == "running":
        return 2
    elif gcode_ready:
        return 1
    return 0


def get_sensor_status(model_id: int):
    """
    Get sensor status of a model
    """
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT status FROM process WHERE model_id = %s ORDER BY start DESC LIMIT 1"
    cursor.execute(query, (model_id,))
    sensor_status = cursor.fetchone()
    cursor.close()
    cnx.close()
    if sensor_status is not None:
        return sensor_status[0]
    return sensor_status


def model_id_to_filename(_model_id: int):
    """
    Get filename from model id
    """
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT filename FROM model WHERE id = %s"
    cursor.execute(query, (_model_id,))
    filename = cursor.fetchone()[0]
    cursor.close()
    cnx.close()
    return filename


def filename_to_model_id(filename: str):
    """
    Get model id from filename
    """
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM model WHERE filename = %s"
    cursor.execute(query, (filename,))
    _model_id = cursor.fetchone()[0]
    cursor.close()
    cnx.close()
    return _model_id


def model_exists(filename: str):
    """
    Check if model exists
    """
    return os.path.exists(f"{MODEL_PATH}/{filename}")
