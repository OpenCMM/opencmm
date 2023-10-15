from cncmark.line import (
    get_sides,
)
from cncmark.edge import (
    import_edges,
)


def test_import_edges():
    sides = get_sides()
    import_edges(sides)
