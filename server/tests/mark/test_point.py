from server.mark.point import (
    ray_cast,
    Shape,
    get_visible_lines,
    get_lines_on_coplanar_facets,
    get_visible_facets,
    group_by_coplanar_facets,
)


def test_ray_cast():
    assert ray_cast("tests/fixtures/stl/sample.stl", (0, 0, 20))
    assert not ray_cast("tests/fixtures/stl/sample.stl", (0, 100, 20))
    assert not ray_cast("tests/fixtures/stl/sample.stl", (-10, 30, 20))


def test_get_shapes():
    shape = Shape("tests/fixtures/stl/sample.stl")
    lines, arcs = shape.get_shapes()
    assert len(lines) == 8
    assert len(arcs) == 5


def test_get_shapes_with_step_slope():
    shape = Shape("tests/fixtures/stl/step.STL")
    lines, arcs = shape.get_shapes()
    assert len(lines) == 8
    assert len(arcs) == 0


def test_get_visible_lines():
    lines = get_visible_lines("tests/fixtures/stl/step.STL")
    assert len(lines) == 14


def test_group_by_coplanar_facets():
    facets = get_visible_facets("tests/fixtures/stl/step.STL")
    coplanar_facets = group_by_coplanar_facets(facets)
    assert len(coplanar_facets) == 3


def test_get_lines_on_coplanar_facets():
    facets = get_visible_facets("tests/fixtures/stl/step.STL")
    lines = get_lines_on_coplanar_facets(facets)
    assert len(lines) == 3
    for facet_lines in lines:
        assert len(facet_lines) == 2
        for pair in facet_lines:
            assert len(pair) == 2
