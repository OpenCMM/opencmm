import random
from cncmark.config import MYSQL_CONFIG
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


def get_edges():
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT * FROM edge"
    cursor.execute(query)
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


def get_edges_by_side_id(side_id: int):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    query = "SELECT rx,ry,rz FROM edge WHERE side_id = %s"
    cursor.execute(query, (side_id,))
    edges = cursor.fetchall()
    cursor.close()
    cnx.close()
    return edges


def get_edge_path(
    length: float = 2.5,
    measure_feedrate: float = 300,
    move_feedrate: float = 600,
    xyz_offset: tuple = (0, 0, 0),
):
    path = []
    edges = get_edges()
    for edge in edges:
        edge_id, side_id, arc_id, x, y, z, rx, ry, rz = edge
        if arc_id is None:
            side_id, x0, y0, z0, x1, y1, z1, pair_id = get_side(side_id)
            direction = get_direction(x0, y0, x1, y1)

            (x, y, z) = (x + xyz_offset[0], y + xyz_offset[1], z + xyz_offset[2])

            if direction == 0:
                py0 = y - length
                py1 = y + length
                path.append(
                    [
                        f"G1 X{x} Y{py0} Z{z} F{move_feedrate}",
                        f"G1 X{x} Y{py1} Z{z} F{measure_feedrate}",
                        x,
                        y,
                    ]
                )

            elif direction == 1:
                px0 = x - length
                px1 = x + length
                path.append(
                    [
                        f"G1 X{px0} Y{y} Z{z} F{move_feedrate}",
                        f"G1 X{px1} Y{y} Z{z} F{measure_feedrate}",
                        x,
                        y,
                    ]
                )

        else:
            assert side_id is None
            arc_id, radius, cx, cy, cz, rradius, rcx, rcy, rcz = get_arc(arc_id)
            point1, point2 = get_arc_path((cx, cy, cz), (x, y, z), length)
            point1 = [x + xyz_offset[i] for i, x in enumerate(point1)]
            point2 = [x + xyz_offset[i] for i, x in enumerate(point2)]
            path.append(
                [
                    f"G1 X{point1[0]} Y{point1[1]} Z{point1[2]} F{move_feedrate}",
                    f"G1 X{point2[0]} Y{point2[1]} Z{point2[2]} F{measure_feedrate}",
                    x,
                    y,
                ]
            )

    return sorted(path, key=lambda point: (point[2], point[3]))


def generate_gcode(path):
    # avoid duplicate gcode
    random_4_digit = str(random.randint(1000, 9999))
    gcode = ["%", f"O{random_4_digit}"]
    for row in path:
        gcode.append(row[0])
        gcode.append(row[1])
    return gcode + ["M30", "%"]


def save_gcode(gcode, file_path: str):
    with open(file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")
