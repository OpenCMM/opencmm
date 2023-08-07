from mark.point import get_lines, get_unique_points


def test_get_lines():
    z = 10.0
    lines = get_lines("tests/fixtures/stl/sample.stl", z)
    assert len(lines) == 8
    for line in lines:
        assert line.shape == (2, 3)
        assert line[0][2] == z
        assert line[1][2] == z


def test_get_unique_points():
    z = 10.0
    unique_points = get_unique_points("tests/fixtures/stl/sample.stl", z)
    assert len(unique_points) == 12
    for point in unique_points:
        assert point.shape == (3,)
        assert point[2] == z
