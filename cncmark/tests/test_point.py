from cncmark.point import (
    get_shapes,
    get_unique_points,
    import_points,
    get_highest_z,
)
from stl import mesh


def test_get_unique_points():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    unique_points = get_unique_points(lines, arcs)
    assert len(unique_points) == 23
    for point in unique_points:
        assert point.shape == (3,)
        assert point[2] == z


def test_import_points():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    unique_points = get_unique_points(lines, arcs)
    import_points(unique_points)


def test_get_highest_point():
    cuboid = mesh.Mesh.from_file("tests/fixtures/stl/sample.stl")
    # get vertices
    vertices = cuboid.vectors
    highest_z = get_highest_z(vertices)
    assert highest_z == 10.0
