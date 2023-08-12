import numpy as np
class GCode:
    def __init__(self, points, feed_rate=1000):
        self.points = points
        self.feed_rate = feed_rate
        self.gcode = []
        self.pic_wait = []

    def generate_gcode(self):
        start = np.array([0, 0, 0])
        f_per_sec = self.feed_rate / 60
        for point in self.points:
            # wait 1 second
            self.gcode.append("G4 P1")

            time_to_move = self.distance(start, point) / f_per_sec
            self.pic_wait.append(1 + time_to_move)
            one_line = f"G1 X{point[0]} Y{point[1]} Z{point[2]} F{self.feed_rate}"
            self.gcode.append(one_line)
            start = point

    def save_gcode(self, file_path: str):
        with open(file_path, "w") as f:
            for line in self.gcode:
                f.write(line + "\n")

    def distance(self, a, b):
        return np.linalg.norm(a - b)
