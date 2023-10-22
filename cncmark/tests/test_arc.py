from cncmark.point import get_shapes
from cncmark.arc import import_arcs

def test_import_arcs():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    import_arcs(arcs)
