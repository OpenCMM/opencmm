import numpy as np


class GCode:
    def __init__(self, points, feed_rate, camera_height):
        """
        :param points: numpy array of points
        :param feed_rate: feed rate in mm/min
        :param camera_height: height of camera in mm
        :return: GCode object
        """
        self.points = points
        self.feed_rate = feed_rate
        self.camera_height = camera_height
        self.gcode = []
        self.camera_wait = []

    def generate_gcode(self):
        start = np.array([0, 0, 0])
        f_per_sec = self.feed_rate / 60
        for point in self.points:
            # wait 1 second
            self.gcode.append("G4 P1")

            time_to_move = self.distance(start, point) / f_per_sec
            self.camera_wait.append(1 + time_to_move)
            z = point[2] + self.camera_height
            one_line = f"G1 X{point[0]} Y{point[1]} Z{z} F{self.feed_rate}"
            self.gcode.append(one_line)
            start = point

    def save_gcode(self, file_path: str):
        with open(file_path, "w") as f:
            for line in self.gcode:
                f.write(line + "\n")

    def distance(self, a, b):
        return np.linalg.norm(a - b)
