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


def get_trace_line_id_from_line_number(mysql_config: dict, model_id: int, line: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "SELECT trace_line.id FROM `trace` INNER JOIN trace_line ON "
        "trace.id = trace_line.trace_id "
        "WHERE trace.model_id = %s AND trace_line.line = %s "
        "LIMIT 1"
    )
    cursor.execute(
        query,
        (
            model_id,
            line,
        ),
    )
    trace_line_id = cursor.fetchone()
    cursor.close()
    cnx.close()
    if trace_line_id is None:
        return None
    return trace_line_id[0]


def import_traces(mysql_config: dict, traces: list):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO trace "
        "(model_id, type, start, end, result) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, traces)
    cnx.commit()
    cursor.close()
    cnx.close()
