from server.coordinate import Coordinate
from server.camera import Camera
from server.line import Line
from server.arc import Arc, get_arc_info
from .single import SingleImage
import cv2
import numpy as np
import mysql.connector
from server.config import MYSQL_CONFIG


class AllImages:
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        self.previous_lines = []
        self.lines = []
        self.arcs = []

    def add_image(self, image, distance: float, center: Coordinate) -> None:
        single = SingleImage(image, center, self.camera)
        lines = single.lines(distance)
        if lines is None:
            return None

        if len(self.previous_lines) == 0:
            self.previous_lines = lines
            return None

        for line in lines:
            is_new_line = True
            for i, previous_line in enumerate(self.previous_lines):
                new_line = line.connect_lines(previous_line)
                if new_line is not None:
                    self.previous_lines[i] = new_line
                    is_new_line = False
                    break

            if is_new_line:
                self.previous_lines.append(line)

    def save_image(self, path: str) -> None:
        entire_image = np.asarray([[[0, 0, 0]] * 1200] * 1000, dtype=np.uint8)
        for line in self.lines:
            start = line.start
            end = line.end
            cv2.line(
                entire_image,
                (int((start.x + 100) * 5), int((-start.y + 100) * 5)),
                (int((end.x + 100) * 5), int((-end.y + 100) * 5)),
                (255, 255, 255),
                1,
            )
            cv2.putText(
                entire_image,
                f"{line.get_length():.3f} mm",
                (
                    int((start.x + end.x + 200) * 5 / 2),
                    int((-start.y - end.y + 200) * 5 / 2),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (105, 145, 209),
                1,
            )
        for arc in self.arcs:
            cv2.circle(
                entire_image,
                (int((arc.center.x + 100) * 5), int((-arc.center.y + 100) * 5)),
                int(arc.radius * 5),
                (255, 255, 255),
                1,
            )
            cv2.putText(
                entire_image,
                f"({arc.center.x:.4f}, {arc.center.y:.4f}) | r: {arc.radius:.4f}",
                (
                    int((arc.center.x + 100) * 5),
                    int((-arc.center.y + 100) * 5),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (105, 145, 209),
                1,
            )
        cv2.imwrite(path, entire_image)

    def fetch_real_coordinates(self) -> dict:
        cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
        cursor = cnx.cursor()

        real_coordinates = {}
        query = """
            SELECT point_id, rx, ry, rz
            FROM point
        """
        cursor.execute(query)
        for r in cursor:
            real_coordinates[r[0]] = Coordinate(r[1], r[2], r[3])

        cursor.close()
        cnx.close()

        return real_coordinates

    def fetch_lines(self):
        cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
        cursor = cnx.cursor()

        lines = []
        query = """
            SELECT a, b
            FROM line
        """
        cursor.execute(query)
        for line in cursor:
            lines.append((line[0], line[1]))

        cursor.close()
        cnx.close()

        return lines

    def add_lines(self):
        real_coordinates = self.fetch_real_coordinates()
        lines = self.fetch_lines()
        for line in lines:
            start = real_coordinates[line[0]]
            end = real_coordinates[line[1]]
            self.lines.append(Line(start, end))

    def fetch_arcs(self):
        cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
        cursor = cnx.cursor()

        arcs = []
        query = """
            SELECT a, b, c, d
            FROM arc
        """
        cursor.execute(query)
        for arc in cursor:
            arcs.append((arc[0], arc[1], arc[2], arc[3]))

        cursor.close()
        cnx.close()

        return arcs

    def add_arcs(self):
        real_coordinates = self.fetch_real_coordinates()
        arcs = self.fetch_arcs()
        for arc in arcs:
            arc_points = np.array([real_coordinates[point_id] for point_id in arc])
            radius, center = get_arc_info(arc_points)
            center = Coordinate(center[0], center[1], center[2])
            self.arcs.append(Arc(radius, center))
