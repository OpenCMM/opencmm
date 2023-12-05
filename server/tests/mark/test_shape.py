from server.mark.shape import Shape


def test_group_by_coplanar_facets():
    shape = Shape("tests/fixtures/stl/sample.stl")
    visible_facets = shape.get_visible_facets()
    facet_groups = shape.group_by_coplanar_facets(visible_facets)
    assert len(facet_groups) == 1

    shape = Shape("tests/fixtures/stl/step.STL")
    visible_facets = shape.get_visible_facets()
    facet_groups = shape.group_by_coplanar_facets(visible_facets)
    assert len(facet_groups) == 3


def test_get_shapes():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()

    assert len(lines) == 1
    assert len(arcs) == 1

    assert len(lines[0]) == 8
    assert len(arcs[0]) == 5


def test_get_shapes_with_step_slope():
    shape = Shape("tests/fixtures/stl/step.STL")
    lines, arcs = shape.get_shapes()

    assert len(lines) == 3
    assert len(arcs) == 0

    # assert len(lines[0]) == 4
    # assert len(lines[1]) == 4
    # assert len(lines[2]) == 4
