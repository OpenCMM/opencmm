import numpy as np


class Coordinate(np.ndarray):
    def __new__(cls, x, y, z):
        obj = np.array([x, y, z], dtype=float).view(cls)
        return obj

    def __init__(self, x, y, z):
        self.x = self[0]
        self.y = self[1]
        self.z = self[2]

    def __repr__(self):
        return f"Coordinate(x={self.x}, y={self.y}, z={self.z})"

    def __add__(self, other):
        return Coordinate(*super().__add__(other))

    def __sub__(self, other):
        return Coordinate(*super().__sub__(other))

    def __mul__(self, other):
        return Coordinate(*super().__mul__(other))

    def __truediv__(self, other):
        return Coordinate(*super().__truediv__(other))

    def distance_to(self, other) -> float:
        return np.linalg.norm(self - other)

    def unique_key(self) -> str:
        return f"{self.x},{self.y},{self.z}"
