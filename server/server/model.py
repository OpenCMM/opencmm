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
        idx = model[0] 
        filename = model[1]
        model_path = os.path.join(MODEL_PATH, filename)
        model_size = os.path.getsize(model_path)
        model_modified_time = int(os.path.getmtime(model_path) * 1000)
        gcode_ready = os.path.exists(f"data/gcode/{filename}.gcode")
        models_data.append(
            {
                "id": idx,
                "name": filename,
                "size": model_size,
                "modified_time": model_modified_time,
                "gcode_ready": gcode_ready,
            }
        )
    return models_data


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
