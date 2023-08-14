from cncmark.point import (
    get_shapes,
    get_unique_points,
    import_points,
    get_highest_point,
)


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
    highest_point = get_highest_point("tests/fixtures/stl/sample.stl")
    assert highest_point[2][2] == 10.0
