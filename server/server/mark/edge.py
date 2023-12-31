import mysql.connector
from server.config import MODEL_PATH
import networkx as nx
from .line import get_side
from .arc import get_arc
import math
from .point import ray_cast
from .gcode import to_gcode_row


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


def get_edges_by_side_id(side_id: int, mysql_config: dict, process_id: int):
    """
    Get edge results by side_id and process_id
    """
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


def get_edge_id_from_line_number(mysql_config: dict, model_id: int, line_number: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "SELECT id FROM edge WHERE model_id = %s AND line = %s"
    cursor.execute(query, (model_id, line_number))
    edge_ids = cursor.fetchall()
    cursor.close()
    cnx.close()
    if edge_ids:
        return [row[0] for row in edge_ids]


class EdgePath:
    def __init__(
        self,
        mysql_config: dict,
        model_id: int,
        stl_filename: str,
        measure_config: tuple,
    ):
        self.mysql_config = mysql_config
        self.model_id = model_id
        self.stl_filename = stl_filename
        self.range = measure_config[0]
        self.measure_feedrate = measure_config[1]
        self.move_feedrate = measure_config[2]

    def get_line_edge_path(
        self,
        side_id: int,
        xyz: tuple,
        xyz_offset: tuple,
    ):
        x, y, z = xyz
        side_id, model_id, x0, y0, z0, x1, y1, z1, pair_id = get_side(
            side_id, self.mysql_config
        )
        direction = get_direction(x0, y0, x1, y1)
        if direction == 0:
            hit = ray_cast(
                f"{MODEL_PATH}/{self.stl_filename}",
                (x - xyz_offset[0], y + self.range - xyz_offset[1], 1000),
            )
            py0, py1 = (
                (y - self.range, y + self.range)
                if hit
                else (y + self.range, y - self.range)
            )
            return [
                to_gcode_row(x, py0, self.move_feedrate),
                to_gcode_row(x, py1, self.measure_feedrate),
                x,
                y,
                z,
            ]

        elif direction == 1:
            hit = ray_cast(
                f"{MODEL_PATH}/{self.stl_filename}",
                (x + self.range - xyz_offset[0], y - xyz_offset[1], 1000),
            )
            px0, px1 = (
                (x - self.range, x + self.range)
                if hit
                else (x + self.range, x - self.range)
            )
            return [
                to_gcode_row(px0, y, self.move_feedrate),
                to_gcode_row(px1, y, self.measure_feedrate),
                x,
                y,
                z,
            ]

    def get_arc_path(self, center, xyz, distance):
        cx, cy, cz = center
        x, y, z = xyz
        # Calculate the direction vector from the center to point A
        direction_vector = (x - cx, y - cy, z - cz)

        # Calculate the magnitude of the direction vector
        magnitude = math.sqrt(
            direction_vector[0] ** 2
            + direction_vector[1] ** 2
            + direction_vector[2] ** 2
        )

        # Normalize the direction vector
        normalized_direction = (
            direction_vector[0] / magnitude,
            direction_vector[1] / magnitude,
            direction_vector[2] / magnitude,
        )

        outside_point = (
            x + distance * normalized_direction[0],
            y + distance * normalized_direction[1],
            z + distance * normalized_direction[2],
        )
        inside_point = (
            x - distance * normalized_direction[0],
            y - distance * normalized_direction[1],
            z - distance * normalized_direction[2],
        )
        # round to 3 decimal places
        outside_point = [round(x, 3) for x in outside_point]
        inside_point = [round(x, 3) for x in inside_point]
        return outside_point, inside_point

    def get_arc_edge_path(
        self,
        arc_id: int,
        xyz: tuple,
        xyz_offset: tuple,
    ):
        x, y, z = xyz
        arc_id, model_id, radius, cx, cy, cz = get_arc(arc_id, self.mysql_config)
        # add offset to center
        (cx, cy, cz) = (
            cx + xyz_offset[0],
            cy + xyz_offset[1],
            cz + xyz_offset[2],
        )
        outside_point, inside_point = self.get_arc_path(
            (cx, cy, cz), (x, y, z), self.range
        )
        hit = ray_cast(
            f"{MODEL_PATH}/{self.stl_filename}",
            (
                outside_point[0] - xyz_offset[0],
                outside_point[1] - xyz_offset[1],
                1000,
            ),
        )
        first, second = (
            (inside_point, outside_point) if hit else (outside_point, inside_point)
        )
        return [
            to_gcode_row(first[0], first[1], self.move_feedrate),
            to_gcode_row(second[0], second[1], self.measure_feedrate),
            x,
            y,
            z,
        ]

    def delete_overlap_edges(self, optimal_path: list):
        """
        Delete edges with the same x, y value and
        keep the one with the highest z value
        """
        path = []
        prev_xy = None
        prev_z = None
        for row in optimal_path:
            _xy = (row[2], row[3])
            if _xy == prev_xy:
                if prev_z > row[4]:
                    continue
                else:
                    path.pop()

            prev_xy = _xy
            prev_z = row[4]
            path.append(row)
        return path

    def add_line_number_from_path(self, optimal_path: list):
        cnx = mysql.connector.connect(**self.mysql_config, database="coord")
        cursor = cnx.cursor()
        cursor = cnx.cursor()
        update_list = []
        prev_xy = None
        prev_line_number = None
        initial_line_number = 4
        idx = 0
        for row in optimal_path:
            edge_id = row[5]
            _xy = (row[2], row[3])
            if _xy == prev_xy:
                update_list.append((prev_line_number, edge_id))
            else:
                current_line_number = initial_line_number + idx * 2
                update_list.append((current_line_number, edge_id))
                prev_line_number = current_line_number
                idx += 1
                prev_xy = _xy

        query = "UPDATE edge SET line = %s WHERE id = %s"
        cursor.executemany(query, update_list)
        cnx.commit()
        cursor.close()
        cnx.close()
        return cursor.rowcount

    def get_edge_path(
        self,
        xyz_offset: tuple = (0, 0, 0),
        update_data: bool = True,
    ):
        path = []
        edges = get_edges(self.mysql_config, self.model_id)
        for edge in edges:
            edge_id, model_id, side_id, arc_id, x, y, z, _line = edge
            # add offset
            (x, y, z) = (x + xyz_offset[0], y + xyz_offset[1], z + xyz_offset[2])
            if arc_id is None:
                line_edge_path = self.get_line_edge_path(
                    side_id,
                    (x, y, z),
                    xyz_offset,
                )
                line_edge_path.append(edge_id)
                path.append(line_edge_path)
            else:
                assert side_id is None
                arc_edge_path = self.get_arc_edge_path(
                    arc_id,
                    (x, y, z),
                    xyz_offset,
                )
                arc_edge_path.append(edge_id)
                path.append(arc_edge_path)

        optimal_path = sorted(path, key=lambda point: (point[2], point[3]))
        # calculate the shortest path
        G = nx.Graph()
        for i, row in enumerate(optimal_path):
            G.add_node(i, pos=(row[2], row[3]))
        for i in range(len(optimal_path)):
            for j in range(i + 1, len(optimal_path)):
                weight = (
                    (optimal_path[i][2] - optimal_path[j][2]) ** 2
                    + (optimal_path[i][3] - optimal_path[j][3]) ** 2
                ) ** 0.5
                G.add_edge(i, j, weight=weight)

        # Find the optimal path using the Travelling Salesman Problem (TSP)
        tour = nx.approximation.traveling_salesman_problem(G, cycle=False)
        optimal_path = [optimal_path[node] for node in tour]

        if update_data:
            self.add_line_number_from_path(optimal_path)
        return self.delete_overlap_edges(optimal_path)


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


def delete_edge_results(mysql_config: dict, process_id: int):
    cnx = mysql.connector.connect(**mysql_config, database="coord")
    cursor = cnx.cursor()
    query = "DELETE FROM edge_result WHERE process_id = %s"
    cursor.execute(query, (process_id,))
    cnx.commit()
    cursor.close()
    cnx.close()
