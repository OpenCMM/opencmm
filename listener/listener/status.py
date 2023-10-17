import mysql.connector

def start_measuring(mysql_config: dict, status: str):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "INSERT INTO process(status) VALUES (%s)", (status,)
    )
    processs_id = mysql_cur.lastrowid
    mysql_conn.commit()
    mysql_cur.close()
    mysql_conn.close()
    return processs_id

def update_process_status(mysql_config: dict, process_id: int, status: str):
    mysql_conn = mysql.connector.connect(**mysql_config, database="coord")
    mysql_cur = mysql_conn.cursor()
    mysql_cur.execute(
        "UPDATE process SET status = %s WHERE id = %s", (status, process_id, )
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