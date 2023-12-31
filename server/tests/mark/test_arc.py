from server.mark.point import Shape
from server.mark.arc import (
    add_measured_arc_info,
    fit_circle,
    get_arc_info,
    get_edges_for_arc,
)
from server.config import MYSQL_CONFIG
import pytest


def test_fit_circle():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()
    for arc_points in arcs:
        points = arc_points[:, :2]
        center_x, center_y, radius = fit_circle(points)


def test_get_arc_info():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()
    for arc_points in arcs:
        get_arc_info(arc_points)


def test_get_edges_for_arc():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()
    for arc_points in arcs:
        edges = get_edges_for_arc(1, 1, arc_points, 3)
        assert len(edges) == 3


def test_get_edges_for_arc_many_edges():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()
    for arc_points in arcs:
        edges = get_edges_for_arc(1, 1, arc_points, 4)
        assert len(edges) == 4

        edges = get_edges_for_arc(1, 1, arc_points, 6)
        assert len(edges) == 6


@pytest.mark.skip(reason="not implemented")
def test_add_measured_arc_info():
    add_measured_arc_info(2, MYSQL_CONFIG)
