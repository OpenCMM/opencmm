import cv2
import numpy as np
from server.coordinate import Coordinate


class Line:
    def __init__(self, start: Coordinate, end: Coordinate) -> None:
        # start.x < end.x
        if start.x > end.x:
            self.start = end
            self.end = start
        else:
            self.start = start
            self.end = end

    def get_slope(self) -> float:
        if abs(self.start.x - self.end.x) < 0.1:
            return np.inf
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def get_slope_diff(self, other: "Line") -> float:
        if self.get_slope() == other.get_slope():
            return 0
        return abs(self.get_slope() - other.get_slope())

    def get_intercept(self) -> float:
        if self.get_slope() == np.inf:
            return np.inf
        return self.start.y - self.get_slope() * self.start.x

    def get_intercept_diff(self, other: "Line") -> float:
        if self.get_intercept() == other.get_intercept():
            return 0
        return abs(self.get_intercept() - other.get_intercept())

    def get_x(self, y: float) -> float:
        return (y - self.get_intercept()) / self.get_slope()

    def get_y(self, x: float) -> float:
        return self.get_slope() * x + self.get_intercept()

    def get_length(self) -> float:
        length = np.sqrt(
            (self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2
        )
        return float(length)

    def get_intersection(self, other) -> tuple:
        x = (other.get_intercept() - self.get_intercept()) / (
            self.get_slope() - other.get_slope()
        )
        y = self.get_slope() * x + self.get_intercept()
        return (x, y)

    def is_same_straight_line(self, other: "Line") -> bool:
        slope_diff = self.get_slope_diff(other)
        intercept_diff = self.get_intercept_diff(other)
        if self.get_slope() == np.inf and other.get_slope() == np.inf:
            return abs(self.start.x - other.start.x) < 0.2
        return slope_diff < 0.1 and intercept_diff < 0.1

    def is_x_overlapping(self, other: "Line") -> bool:
        return (
            self.start.x <= other.start.x <= self.end.x
            or self.start.x <= other.end.x <= self.end.x
            or other.start.x <= self.start.x <= other.end.x
            or other.start.x <= self.end.x <= other.end.x
        )

    def is_y_overlapping(self, other: "Line") -> bool:
        return (
            self.start.y <= other.start.y <= self.end.y
            or self.end.y <= other.start.y <= self.start.y
            or self.start.y <= other.end.y <= self.end.y
            or self.end.y <= other.end.y <= self.start.y
            or other.start.y <= self.start.y <= other.end.y
            or other.end.y <= self.start.y <= other.start.y
            or other.start.y <= self.end.y <= other.end.y
            or other.end.y <= self.start.y <= other.start.y
        )

    def is_overlapping(self, other: "Line") -> bool:
        if self.get_slope() == np.inf and other.get_slope() == np.inf:
            return self.is_y_overlapping(other)
        if self.get_slope() == 0 and other.get_slope() == 0:
            return self.is_x_overlapping(other)
        return self.is_x_overlapping(other) and self.is_y_overlapping(other)

    def connect_lines(self, other: "Line") -> "Line" or None:
        if self.is_same_straight_line(other) and self.is_overlapping(other):
            return Line(
                Coordinate(
                    min(self.start.x, other.start.x),
                    min(self.start.y, other.start.y),
                    self.start.z,
                ),
                Coordinate(
                    max(self.end.x, other.end.x),
                    max(self.end.y, other.end.y),
                    self.start.z,
                ),
            )

    def __repr__(self) -> str:
        return f"Line({self.start}, {self.end})"


def get_lines(
    image,
    gaussian_blur_size=5,
    canny_low_threshold=100,
    canny_high_threshold=200,
    rho=0.1,
    hough_threshold=100,
    min_line_length=50,
    max_line_gap=200,
):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (gaussian_blur_size, gaussian_blur_size), 0)
    edges = cv2.Canny(
        blur_gray,
        canny_low_threshold,
        canny_high_threshold,
        apertureSize=3,
        L2gradient=True,
    )
    edges = cv2.dilate(edges, None, iterations=1)
    edges = cv2.erode(edges, None, iterations=1)

    lines = cv2.HoughLinesP(
        edges,
        rho,
        np.pi / 180 * rho,
        hough_threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )
    return lines
