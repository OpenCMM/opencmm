import numpy as np
import trimesh


class MockSensor:
    def __init__(self, stl_filepath: str, middle_sensor_output: int = 9100):
        self.mesh = trimesh.load_mesh(stl_filepath)
        self.ray_directions = np.array([[0, 0, -1]])
        self.middle_sensor_output = middle_sensor_output

    def get_distance(self, xyz: tuple):
        ray_origins = np.array([xyz])
        locations = self.mesh.ray.intersects_location(ray_origins, self.ray_directions)[
            0
        ]
        if locations is None:
            return None
        # location with the highest z value is the closest point
        location = locations[np.argmax(locations[:, 2])]
        distance = np.linalg.norm(np.array(xyz) - location)
        return distance

    def get_sensor_output(self, xyz: tuple):
        distance = self.get_distance(xyz)
        if distance is None:
            return None
        # sensor ouputs self.max_sensor_output / 2 when distance is 100
        # if distance is not between 65 ~ 135 mm,
        # sensor outputs 18900
        if 65 <= distance <= 135:
            return self.middle_sensor_output + (100 - distance) * (
                self.middle_sensor_output / 35
            )
        else:
            return 18900

    def get_fluctuating_sensor_output(self, xyz: tuple, fluctuation: float = 0.1):
        distance = self.get_distance(xyz)
        if distance is None:
            return None
        # sensor ouputs self.max_sensor_output / 2 when distance is 100
        # if distance is not between 65 ~ 135 mm,
        # sensor outputs 18900
        if 65 <= distance <= 135:
            return self.middle_sensor_output + (100 - distance) * (
                self.middle_sensor_output / 35
            ) * (1 + fluctuation * np.random.randn())
        else:
            return 18900
