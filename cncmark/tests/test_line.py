from cncmark.point import get_shapes
from cncmark.line import (
    import_lines,
    get_parallel_lines,
    get_pairs,
    import_sides,
    get_sides,
)
from cncmark.edge import (
    import_edges_from_sides,
    get_edge_path,
    generate_gcode,
    save_gcode,
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


def test_get_sides():
    sides = get_sides()
    assert len(sides) == 8


def test_import_edges():
    sides = get_sides()
    import_edges_from_sides(sides)
    path = get_edge_path(sides)
    assert len(path) == 8


def test_generate_gcode():
    sides = get_sides()
    path = get_edge_path(sides)
    gcode = generate_gcode(path)
    save_gcode(gcode, "tests/fixtures/gcode/edge.gcode")
