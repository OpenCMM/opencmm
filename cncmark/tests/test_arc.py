from cncmark.point import get_shapes
from cncmark.arc import add_measured_arc_info, fit_circle
from .config import MYSQL_CONFIG
import pytest


def test_fit_circle():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    for arc_points in arcs:
        points = arc_points[:, :2]
        center_x, center_y, radius = fit_circle(points)


@pytest.mark.skip(reason="not implemented")
def test_add_measured_arc_info():
    add_measured_arc_info(1, MYSQL_CONFIG)
