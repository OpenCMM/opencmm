from cncmark.config import MYSQL_CONFIG
import mysql.connector
from mysql.connector.errors import IntegrityError
import random


def get_edges_for_side(side: tuple, number_of_edges_per_side: int) -> list:
    """
    Returns a list of edges for a side
    Edges need to be distributed evenly along the side
    """
    assert (
        number_of_edges_per_side > 1
    ), "number_of_edges_per_side must be greater than 1"
    side_id, x0, y0, z0, x1, y1, z1, pair_id = side

    edges = []
    for i in range(1, number_of_edges_per_side + 1):
        x = x0 + (x1 - x0) * i / (number_of_edges_per_side + 1)
        y = y0 + (y1 - y0) * i / (number_of_edges_per_side + 1)
        z = z0 + (z1 - z0) * i / (number_of_edges_per_side + 1)
        # x, y, z need to be rounded to 3 decimal places
        x, y, z = round(x, 3), round(y, 3), round(z, 3)
        edges.append((side_id, x, y, z))

    return edges


def to_edge_list(sides: list, number_of_edges_per_side: int):
    edge_list = []
    for side in sides:
        edge_list += get_edges_for_side(side, number_of_edges_per_side)

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
        print("Error: unable to import edges")
    cnx.commit()
    cursor.close()
    cnx.close()


def import_edges_from_sides(sides: list, number_of_edges_per_side: int = 2):
    edge_list = to_edge_list(sides, number_of_edges_per_side)
    import_edges(edge_list)


def get_direction(x0, y0, x1, y1):
    if y0 == y1:
        return 0
    elif x0 == x1:
        return 1
    else:
        return -1


def get_edge_path(
    sides,
    length: float = 2.5,
    measure_feedrate: float = 300,
    move_feedrate: float = 600,
    xyz_offset: tuple = (0, 0, 0),
):
    path = []
    for side in sides:
        # path is the diagonal line of the side that crosses the center of the side
        side_id, x0, y0, z0, x1, y1, z1, pair_id = side
        direction = get_direction(x0, y0, x1, y1)

        # get center of side
        for _, x, y, z in get_edges_for_side(side, 2):
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
