from cncmark.point import get_shapes
from cncmark.line import (
    get_parallel_lines,
    get_pairs,
    import_sides,
    get_sides,
    import_edges_from_sides,
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    save_gcode,
)
from cncmark.arc import import_arcs
from .config import MYSQL_CONFIG


def test_get_lines():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    assert len(lines) == 8
    assert len(arcs) == 5
    for line in lines:
        assert line.shape == (2, 3)


def test_get_parallel_lines():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    x, y, other = get_parallel_lines(lines)
    assert len(x) == 4
    assert len(y) == 4

    pairs = get_pairs(x, 0)
    assert len(pairs) == 2
    import_sides(pairs, "line", MYSQL_CONFIG)

    pairs = get_pairs(y, 1)
    assert len(pairs) == 2
    import_sides(pairs, "line", MYSQL_CONFIG)


def test_get_sides():
    sides = get_sides(MYSQL_CONFIG)
    assert len(sides) == 8


def test_import_edges():
    sides = get_sides(MYSQL_CONFIG)
    import_edges_from_sides(sides, MYSQL_CONFIG, 2)


def test_import_arcs():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    import_arcs(arcs, MYSQL_CONFIG)


def test_generate_gcode():
    path = get_edge_path(MYSQL_CONFIG)
    gcode = generate_gcode(path)
    save_gcode(gcode, "tests/fixtures/gcode/edge.gcode")
