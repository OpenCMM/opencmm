import mysql.connector
from .line import get_side
from .arc import get_arc
import math


def get_direction(x0, y0, x1, y1):
    if y0 == y1:
        return 0
    elif x0 == x1:
        return 1
    else:
        return -1


def get_edges(mysql_config: dict, model_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM edge WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def get_arc_path(center, xyz, distance):
    cx, cy, cz = center
    x, y, z = xyz
    # Calculate the direction vector from the center to point A
    direction_vector = (x - cx, y - cy, z - cz)

    # Calculate the magnitude of the direction vector
    magnitude = math.sqrt(
        direction_vector[0] ** 2 + direction_vector[1] ** 2 + direction_vector[2] ** 2
    )

    # Normalize the direction vector
    normalized_direction = (
        direction_vector[0] / magnitude,
        direction_vector[1] / magnitude,
        direction_vector[2] / magnitude,
    )

    # Calculate the coordinates of the two points at distance 'distance' from point A
    point1 = (
        x + distance * normalized_direction[0],
        y + distance * normalized_direction[1],
        z + distance * normalized_direction[2],
    )
    point2 = (
        x - distance * normalized_direction[0],
        y - distance * normalized_direction[1],
        z - distance * normalized_direction[2],
    )
    # round to 3 decimal places
    point1 = [round(x, 3) for x in point1]
    point2 = [round(x, 3) for x in point2]
    return point1, point2


def get_edges_by_side_id(side_id: int, mysql_config: dict, process_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "SELECT edge_result.x, edge_result.y, edge_result.z "
        "FROM edge_result INNER JOIN edge ON edge.id = edge_result.edge_id "
        "WHERE edge.side_id = %s AND edge_result.process_id = %s"
    )
    cursor.execute(query, (side_id, process_id))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def to_gcode_row(x, y, feedrate):
    # round to 3 decimal places
    x = round(x, 3)
    y = round(y, 3)
    return f"G1 X{x} Y{y} F{feedrate}"


def get_edge_path(
    mysql_config: dict,
    model_id: int,
    length: float = 2.5,
    measure_feedrate: float = 300,
    move_feedrate: float = 600,
    xyz_offset: tuple = (0, 0, 0),
):
    path = []
    edges = get_edges(mysql_config, model_id)
    for edge in edges:
        edge_id, model_id, side_id, arc_id, x, y, z = edge
        # add offset
        (x, y, z) = (x + xyz_offset[0], y + xyz_offset[1], z + xyz_offset[2])
        if arc_id is None:
            side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = get_side(
                side_id, mysql_config
            )
            direction = get_direction(x0, y0, x1, y1)
            if direction == 0:
                py0 = y - length
                py1 = y + length
                path.append(
                    [
                        to_gcode_row(x, py0, move_feedrate),
                        to_gcode_row(x, py1, measure_feedrate),
                        x,
                        y,
                    ]
                )

            elif direction == 1:
                px0 = x - length
                px1 = x + length
                path.append(
                    [
                        to_gcode_row(px0, y, move_feedrate),
                        to_gcode_row(px1, y, measure_feedrate),
                        x,
                        y,
                    ]
                )
        else:
            assert side_id is None
            arc_id, model_id, radius, cx, cy, cz = get_arc(arc_id, mysql_config)
            # add offset to center
            (cx, cy, cz) = (cx + xyz_offset[0], cy + xyz_offset[1], cz + xyz_offset[2])
            point1, point2 = get_arc_path((cx, cy, cz), (x, y, z), length)
            path.append(
                [
                    to_gcode_row(point1[0], point1[1], move_feedrate),
                    to_gcode_row(point2[0], point2[1], measure_feedrate),
                    x,
                    y,
                ]
            )
    return sorted(path, key=lambda point: (point[2], point[3]))


def generate_gcode(path, program_number: str):
    gcode = ["%", f"O{program_number}", "G90 G54"]
    for row in path:
        gcode.append(row[0])
        gcode.append(row[1])
    return gcode + ["M30", "%"]


def save_gcode(gcode, file_path: str):
    with open(file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")


def delete_edges_with_model_id(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM edge WHERE model_id = %s"
    cursor.execute(query, (model_id,))
    cnx.commit()
    cursor.close()
    cnx.close()


def get_edge_ids_order_by_x_y(model_id: int, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM edge WHERE model_id = %s ORDER BY x,y"
    cursor.execute(query, (model_id,))
    edge_ids = cursor.fetchall()
    cursor.close()
    cnx.close()
    if edge_ids:
        return [x[0] for x in edge_ids]


def import_edge_results(update_list: list, mysql_config: dict):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = (
        "INSERT INTO edge_result (edge_id, process_id, "
        "x, y, z) VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, update_list)
    cnx.commit()
    cursor.close()
    cnx.close()
