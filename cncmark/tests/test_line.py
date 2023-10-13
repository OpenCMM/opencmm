from cncmark.point import get_shapes
from cncmark.line import import_lines, get_parallel_lines


def test_get_lines():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    assert len(lines) == 8
    assert len(arcs) == 5
    for line in lines:
        assert line.shape == (2, 3)
        assert line[0][2] == z
        assert line[1][2] == z


def test_import_lines():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    import_lines(lines)

def test_get_parallel_lines():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    x, y, other = get_parallel_lines(lines)
    print(x)
    print(y)
    print(other)