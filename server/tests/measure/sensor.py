import numpy as np
import trimesh


class MockSensor:
    def __init__(self, stl_filepath: str, max_sensor_output: int = 18200):
        self.mesh = trimesh.load_mesh(stl_filepath)
        self.ray_directions = np.array([[0, 0, -1]])
        self.max_sensor_output = max_sensor_output

    def get_distance(self, xyz: tuple):
        ray_origins = np.array([xyz])
        location = self.mesh.intersects_location(ray_origins, self.ray_directions)[0][0]
        if location is None:
            return None
        distance = np.linalg.norm(np.array(xyz) - location)
        return distance

    def get_sensor_output(self, xyz: tuple):
        distance = self.get_distance(xyz)
        if distance is None:
            return None
        # if distance is between 65 ~ 135 mm,
        # sensor output self.max_sensor_output * 1.05
        if 65 <= distance <= 135:
            return self.max_sensor_output * 1.05

        # if sensor ouputs self.max_sensor_output / 2 when distance is 100
        return self.max_sensor_output / 2 * (100 / distance)
