from server.mark.point import (
    get_highest_z,
    ray_cast,
    get_shapes,
    get_visible_lines,
)
from stl import mesh


def test_get_highest_point():
    cuboid = mesh.Mesh.from_file("tests/fixtures/stl/sample.stl")
    # get vertices
    vertices = cuboid.vectors
    highest_z = get_highest_z(vertices)
    assert highest_z == 10.0


def test_ray_cast():
    assert ray_cast("tests/fixtures/stl/sample.stl", (0, 0, 20))
    assert not ray_cast("tests/fixtures/stl/sample.stl", (0, 100, 20))
    assert not ray_cast("tests/fixtures/stl/sample.stl", (-10, 30, 20))

def test_get_shapes():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    assert len(lines) == 8
    assert len(arcs) == 5


def test_get_visible_lines():
    lines = get_visible_lines("tests/fixtures/stl/step.STL")
    assert len(lines) == 14
