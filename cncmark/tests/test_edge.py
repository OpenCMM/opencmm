from cncmark.line import (
    get_sides,
)
from cncmark.edge import (
    import_edges,
    to_edge_list,
    get_edge_path,
    generate_gcode,
    save_gcode,
)


def test_import_edges():
    sides = get_sides()
    edge_list = to_edge_list(sides)
    import_edges(edge_list)
    path = get_edge_path(sides)
    assert len(path) == 8


def test_generate_gcode():
    sides = get_sides()
    path = get_edge_path(sides)
    gcode = generate_gcode(path)
    save_gcode(gcode, "tests/fixtures/gcode/edge.gcode")
