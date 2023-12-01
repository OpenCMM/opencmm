import mysql.connector


def get_first_line_number_for_tracing(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT line FROM trace_line WHERE model_id = %s ORDER BY line LIMIT 1"
    cursor.execute(query, (model_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result is None:
        return None
    line = result[0]
    return line
