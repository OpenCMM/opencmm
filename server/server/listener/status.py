import mysql.connector
from server.model import get_model_data


def start_measuring(model_id: int, mysql_config: dict, status: str):
    model_data = get_model_data(model_id)
    offset = (model_data[3], model_data[4], model_data[5])
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "INSERT INTO process(model_id, status, offset_x, offset_y, offset_z) VALUES (%s, %s, %s, %s, %s)",
        (
            model_id,
            status,
            *offset,
        ),
    )
    processs_id = mysql_cur.lastrowid
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()
    return processs_id


def update_process_status(
    mysql_config: dict, process_id: int, status: str, error: str = None
):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "UPDATE process SET status = %s, error = %s WHERE id = %s",
        (
            status,
            error,
            process_id,
        ),
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()


def get_process_status(mysql_config: dict, process_id: int):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute("SELECT * FROM process WHERE id = %s", (process_id,))
    process_status = mysql_cur.fetchone()
    mysql_cur.close()
    mysql_conn.close()
    return process_status


def get_running_process(model_id: int, mysql_config: dict):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "SELECT * FROM process WHERE status = 'running' and model_id = %s", (model_id,)
    )
    process_status = mysql_cur.fetchone()
    mysql_cur.close()
    mysql_conn.close()
    return process_status
