import mysql.connector
from server.model import get_model_data


def start_measuring(model_id: int, mysql_config: dict, status: str):
    model_data = get_model_data(model_id)
    if model_data is None:
        return None
    offset = (model_data[3], model_data[4], model_data[5])
    measurement_range = model_data[6]
    measure_feedrate = model_data[7]
    move_feedrate = model_data[8]
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    query = (
        "INSERT INTO process(model_id, status, x_offset, y_offset, "
        "z_offset, measurement_range, measure_feedrate, move_feedrate) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    mysql_cur.execute(
        query,
        (
            model_id,
            status,
            *offset,
            measurement_range,
            measure_feedrate,
            move_feedrate,
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


def get_process_info(mysql_config: dict, process_id: int):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    query = (
        "SELECT model_id, status, error, start, end, measurement_range, "
        "measure_feedrate, move_feedrate, mtct_latency FROM process WHERE id = %s"
    )
    mysql_cur.execute(query, (process_id,))
    process_info = mysql_cur.fetchone()
    mysql_cur.close()
    mysql_conn.close()
    if process_info is None:
        return None
    start = process_info[3]
    end = process_info[4]
    if end is None:
        duration = None
    else:
        duration = end - start
    process_info = {
        "model_id": process_info[0],
        "status": process_info[1],
        "error": process_info[2],
        "start": start,
        "end": end,
        "duration": duration,
        "measurement_range": process_info[5],
        "measure_feedrate": process_info[6],
        "move_feedrate": process_info[7],
        "mtct_latency": process_info[8],
    }
    return process_info


def get_running_process(model_id: int, mysql_config: dict):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    query = (
        "SELECT * FROM process WHERE status = 'running' " "and model_id = %s LIMIT 1"
    )
    mysql_cur.execute(
        query,
        (model_id,),
    )
    process_status = mysql_cur.fetchone()
    mysql_cur.close()
    mysql_conn.close()
    return process_status


def get_process_list(mysql_config: dict, model_id: int):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute("SELECT * FROM process WHERE model_id = %s", (model_id,))
    process_status = mysql_cur.fetchall()
    mysql_cur.close()
    mysql_conn.close()
    return process_status


def get_prev_next_process(mysql_config: dict, model_id: int, process_id: int):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute("SELECT id FROM process WHERE model_id = %s", (model_id,))
    process_status = mysql_cur.fetchall()
    mysql_cur.close()
    mysql_conn.close()

    prev_process = None
    next_process = None
    for i, process in enumerate(process_status):
        if process[0] == process_id:
            if i > 0:
                prev_process = process_status[i - 1][0]
            if i < len(process_status) - 1:
                next_process = process_status[i + 1][0]
            break
    return prev_process, next_process


def add_end_timestamp(mysql_config: dict, process_id: int):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "UPDATE process SET end = NOW() WHERE id = %s",
        (process_id,),
    )
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()
