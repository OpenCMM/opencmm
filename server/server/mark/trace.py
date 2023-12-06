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


def sort_sides(sides):
    """
    Sort sides by x, y, z
    """
    sorted_sides = []
    for side in sides:
        side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = side
        if x0 < x1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 < y1:
            sorted_sides.append(side)
        elif x0 == x1 and y0 == y1 and z0 < z1:
            sorted_sides.append(side)
        else:
            sorted_sides.append([side_id, model_id, x1, y1, z1, x0, y0, z0, pair_id])
    return sorted_sides


def get_trace_lines(mysql_config: dict, trace_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM trace_line WHERE trace_id = %s"
    cursor.execute(query, (trace_id,))
    trace_lines = cursor.fetchall()
    cursor.close()
    cnx.close()
    return trace_lines


def delete_trace_line_results(trace_id_list: list, cursor, cnx):
    query = (
        "DELETE FROM trace_line_result WHERE trace_line_id "
        "IN (SELECT id FROM trace_line WHERE trace_id = %s)"
    )
    for trace_id in trace_id_list:
        cursor.execute(query, (trace_id,))
        cnx.commit()


def delete_trace_lines(mysql_config: dict, trace_id_list: list):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    delete_trace_line_results(trace_id_list, cursor, cnx)
    query = "DELETE FROM trace_line WHERE trace_id = %s"
    for trace_id in trace_id_list:
        cursor.execute(query, (trace_id,))
        cnx.commit()
    cursor.close()
    cnx.close()


def delete_trace_line_data(mysql_config: dict, model_id: int):
    trace_id_list = get_trace_ids(mysql_config, model_id)
    if trace_id_list is None:
        return
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    delete_trace_line_results(trace_id_list, cursor, cnx)
    query = "DELETE FROM trace_line WHERE trace_id = %s"
    for trace_id in trace_id_list:
        cursor.execute(query, (trace_id,))
        cnx.commit()
    cursor.close()
    cnx.close()


def get_trace_ids(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM trace WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    trace_ids = cursor.fetchall()
    cursor.close()
    cnx.close()
    if trace_ids is None:
        return None
    return [trace_id[0] for trace_id in trace_ids]


def import_trace_lines(mysql_config: dict, trace_lines: list, init_line: int):
    # add line number
    for idx, trace_line in enumerate(trace_lines):
        trace_line.append(init_line + idx * 2)

    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO trace_line (trace_id, x0, y0, x1, y1, z, line) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, trace_lines)
    cnx.commit()
    cursor.close()
    cnx.close()


def import_trace_line_results(mysql_config: dict, step_update_list: list):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO trace_line_result "
        "(trace_line_id, process_id, distance) VALUES (%s, %s, %s)"
    )
    cursor.executemany(query, step_update_list)
    cnx.commit()
    cursor.close()
    cnx.close()
