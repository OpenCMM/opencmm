from server.mark.point import get_shapes
from server.mark.arc import add_measured_arc_info, fit_circle
from .config import MYSQL_CONFIG


def test_fit_circle():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    for arc_points in arcs:
        points = arc_points[:, :2]
        center_x, center_y, radius = fit_circle(points)


def test_add_measured_arc_info():
    add_measured_arc_info(2, MYSQL_CONFIG)
