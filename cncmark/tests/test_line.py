from cncmark.point import get_shapes
from cncmark.line import (
    get_parallel_lines,
    get_pairs,
    import_sides,
    get_sides,
    import_edges_from_sides,
    import_lines,
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    save_gcode,
)
from cncmark.arc import import_arcs
from .config import MYSQL_CONFIG

model_id = 1
model_id_test_part = 1


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
    import_sides(model_id, pairs, "line", MYSQL_CONFIG)

    pairs = get_pairs(y, 1)
    assert len(pairs) == 2
    import_sides(model_id, pairs, "line", MYSQL_CONFIG)


def test_get_sides():
    sides = get_sides(MYSQL_CONFIG)
    assert len(sides) == 8


def test_import_edges():
    sides = get_sides(MYSQL_CONFIG)
    import_edges_from_sides(sides, MYSQL_CONFIG, 2)


def test_import_arcs():
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl")
    import_arcs(model_id, arcs, MYSQL_CONFIG)


def test_generate_gcode():
    program_number = "1001"
    path = get_edge_path(MYSQL_CONFIG, model_id)
    gcode = generate_gcode(path, program_number)
    save_gcode(gcode, "tests/fixtures/gcode/edge.gcode")


def test_import_lines():
    lines, arcs = get_shapes("tests/fixtures/stl/test-Part.stl")
    import_lines(model_id, lines, MYSQL_CONFIG)


def test_import_arcs_with_test_part():
    lines, arcs = get_shapes("tests/fixtures/stl/test-Part.stl")
    import_arcs(model_id_test_part, arcs, MYSQL_CONFIG)
