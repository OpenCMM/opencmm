from cncmark.point import get_shapes
from cncmark.line import (
    import_lines,
    get_parallel_lines,
    get_pairs,
    import_sides,
)


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
    assert len(x) == 4
    assert len(y) == 4

    pairs = get_pairs(x, 0)
    assert len(pairs) == 2
    import_sides(pairs)

    pairs = get_pairs(y, 1)
    assert len(pairs) == 2
    import_sides(pairs)
