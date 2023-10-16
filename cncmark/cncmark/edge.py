from cncmark.config import MYSQL_CONFIG, MEARURE_FEEDRATE, MOVE_FEEDRATE
import mysql.connector
from mysql.connector.errors import IntegrityError


def get_center_of_side(side: tuple):
    side_id, x0, y0, z0, x1, y1, z1, pair_id = side
    x = (x0 + x1) / 2
    y = (y0 + y1) / 2
    z = (z0 + z1) / 2
    return (x, y, z)


def to_edge_list(sides: list):
    edge_list = []
    for side in sides:
        edge_list.append([side[0]] + list(get_center_of_side(side)))

    return order_by_xy(edge_list)


def order_by_xy(edge_list):
    # Sort the list based on x and y values
    return sorted(edge_list, key=lambda point: (point[1], point[2]))


def import_edges(edge_list: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    insert_query = "INSERT INTO edge (side_id, x, y, z) VALUES (%s, %s, %s, %s)"
    try:
        cursor.executemany(insert_query, edge_list)
    except IntegrityError:
        print("Error: unable to import lines")
    cnx.commit()
    cursor.close()
    cnx.close()


def get_direction(x0, y0, x1, y1):
    if y0 == y1:
        return 0
    elif x0 == x1:
        return 1
    else:
        return -1


def get_edge_path(sides, length: float = 2.5):
    path = []
    for side in sides:
        # path is the diagonal line of the side that crosses the center of the side
        side_id, x0, y0, z0, x1, y1, z1, pair_id = side
        direction = get_direction(x0, y0, x1, y1)

        # get center of side
        (x, y, z) = get_center_of_side(side)

        if direction == 0:
            py0 = y - length
            py1 = y + length
            path.append(
                [
                    f"G1 X{x} Y{py0} Z{z} F{MOVE_FEEDRATE}",
                    f"G1 X{x} Y{py1} Z{z} F{MEARURE_FEEDRATE}",
                    x,
                    y,
                ]
            )

        elif direction == 1:
            px0 = x - length
            px1 = x + length
            path.append(
                [
                    f"G1 X{px0} Y{y} Z{z} F{MOVE_FEEDRATE}",
                    f"G1 X{px1} Y{y} Z{z} F{MEARURE_FEEDRATE}",
                    x,
                    y,
                ]
            )

    return sorted(path, key=lambda point: (point[2], point[3]))


def generate_gcode(path):
    gcode = ["O0001"]
    for row in path:
        gcode.append(row[0])
        gcode.append(row[1])
    return gcode + ["M30"]


def save_gcode(gcode, file_path: str):
    with open(file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")
