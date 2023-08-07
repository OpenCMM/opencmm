from mark.point import get_lines


def test_get_lines():
    z = 10.0
    lines = get_lines("tests/fixtures/stl/sample.stl", z)
    assert len(lines) == 8
    for line in lines:
        assert line.shape == (2, 3)
        assert line[0][2] == z
        assert line[1][2] == z
