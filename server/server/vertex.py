import cv2
import numpy as np


def get_vertices(
    image,
    max_corners: int = 1,
    quality_level: float = 0.01,
    min_distance: int = 100,
):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, max_corners, quality_level, min_distance)
    return np.intp(corners)
