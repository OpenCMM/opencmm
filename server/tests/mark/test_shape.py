from server.mark.shape import Shape


def test_are_facets_on_same_plane():
    shape = Shape("tests/fixtures/stl/step.STL")
    assert shape.are_coplanar(7, 8) is True
    assert shape.are_coplanar(7, 11) is False
    assert shape.are_coplanar(11, 12) is True


def test_grounp_by_coplanar_facets():
    shape = Shape("tests/fixtures/stl/sample.stl")
    visible_facet_indices = shape.get_visible_facets()
    group_facets = shape.group_by_coplanar_facets(visible_facet_indices)
    assert len(group_facets) == 1


def test_grounp_by_coplanar_facets_with_step_slope():
    shape = Shape("tests/fixtures/stl/step.STL")
    visible_facet_indices = shape.get_visible_facets()
    group_facets = shape.group_by_coplanar_facets(visible_facet_indices)
    assert len(group_facets) == 3


def test_group_by_coplanar_facets():
    shape = Shape("tests/fixtures/stl/sample.stl")
    visible_facets = shape.get_visible_facets()
    facet_groups = shape.group_by_coplanar_facets(visible_facets)
    assert len(facet_groups) == 1


def test_group_by_coplanar_facets_with_step_slope():
    shape = Shape("tests/fixtures/stl/step.STL")
    visible_facets = shape.get_visible_facets()
    facet_groups = shape.group_by_coplanar_facets(visible_facets)
    assert len(facet_groups) == 3
    assert len(facet_groups[0]) == 2
    assert len(facet_groups[1]) == 2
    assert len(facet_groups[2]) == 2


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

    assert len(lines[0]) == 4
    assert len(lines[1]) == 4
    assert len(lines[2]) == 4
