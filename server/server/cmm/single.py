from server.coordinate import Coordinate
from server.camera import Camera
from .pixel import get_field_of_view, get_pixel_per_mm
import numpy as np
from server.vertex import get_vertices
import mysql.connector
from mysql.connector.errors import IntegrityError
from server.config import MYSQL_CONFIG


class SingleImage:
    def __init__(self, image, center_coordinate: Coordinate, camera: Camera) -> None:
        self.image = image
        # z coordinate is the height of the object
        self.center = center_coordinate
        self.camera = camera

    def get_opencv_origin(self, image, distance: float) -> Coordinate:
        # opencv origin is at top left corner
        pixel_per_mm = self.pixel_per_mm(distance)
        diff_in_pixel = (-image.shape[1] / 2, image.shape[0] / 2, 0)
        diff_in_mm = np.array([x / pixel_per_mm for x in diff_in_pixel])
        return self.center + diff_in_mm

    def pixel_per_mm(self, distance: float) -> float:
        # field_of_view = 10.67
        field_of_view = get_field_of_view(
            self.camera.focal_length, self.camera.sensor_width, distance
        )
        return get_pixel_per_mm(field_of_view, self.image.shape[1])

    def from_opencv_coord(self, distance: float, opencv_xy: tuple) -> Coordinate:
        pixel_per_mm = self.pixel_per_mm(distance)
        opencv_origin = self.get_opencv_origin(self.image, distance)

        return Coordinate(
            opencv_origin.x + opencv_xy[0] / pixel_per_mm,
            opencv_origin.y - opencv_xy[1] / pixel_per_mm,
            self.center.z,
        )

    def from_pixel_length(self, distance: float, pixel_length) -> float:
        pixel_per_mm = self.pixel_per_mm(distance)
        return pixel_length / pixel_per_mm

    def vertex(self, distance: float) -> Coordinate:
        vertices = get_vertices(self.image, 3, 0.1, 2000)
        if vertices is None:
            return None

        center_point_in_pixel = (self.image.shape[1] / 2, self.image.shape[0] / 2)

        # find the vertex closest to the center point
        min_length_to_center_point = np.inf
        for vertext in vertices:
            length_to_center_point = np.linalg.norm(
                np.array(vertext[0]) - np.array(center_point_in_pixel)
            )
            if length_to_center_point < min_length_to_center_point:
                min_length_to_center_point = length_to_center_point
                x, y = vertext[0]

        return self.from_opencv_coord(distance, (x, y))

    def add_real_coordinate(self, distance):
        real_coordinate = self.vertex(distance)
        point_id = self.center.unique_key()

        cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
        cursor = cnx.cursor()

        update_query = """
            UPDATE point
            SET rx = %s, ry = %s, rz = %s
            WHERE point_id = %s
        """
        try:
            data = (
                float(real_coordinate.x),
                float(real_coordinate.y),
                float(real_coordinate.z),
                point_id,
            )
            cursor.execute(update_query, data)
        except IntegrityError:
            print("Error: unable to update points")

        cnx.commit()
        cursor.close()
        cnx.close()
