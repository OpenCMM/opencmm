import mysql.connector


def get_first_line_number_for_tracing(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "SELECT trace_line.line FROM trace_line INNER JOIN trace "
        "ON trace.id = trace_line.trace_id "
        "WHERE trace.model_id = %s ORDER BY line LIMIT 1"
    )
    cursor.execute(query, (model_id,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result is None:
        return None
    line = result[0]
    return line


def get_trace_id_from_line_number(mysql_config: dict, line: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT trace_id FROM trace_line WHERE line = %s"
    cursor.execute(query, (line,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    if result is None:
        return None
    trace_id = result[0]
    return trace_id
