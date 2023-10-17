from cncmark.point import get_shapes
from server.arc import get_arc_info, import_arcs
import pytest
import numpy as np


@pytest.mark.skip(reason="Not implemented")
def test_get_arc_info():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    assert len(lines) == 8
    assert len(arcs) == 5

    first_arc = arcs[0]
    radius, center = get_arc_info(first_arc)
    assert np.isclose(radius, 5.0, atol=1e-6)
    assert np.isclose(center[0], -20.0, atol=1e-6)
    assert np.isclose(center[1], 28.0, atol=1e-6)
    assert np.isclose(center[2], 10.0, atol=1e-6)

    circle = arcs[4]
    radius, center = get_arc_info(circle)
    assert np.isclose(radius, 9.0, atol=1e-6)
    assert np.isclose(center[0], 0.0, atol=1e-6)
    assert np.isclose(center[1], -29.996901, atol=1e-6)
    assert np.isclose(center[2], 10.0, atol=1e-6)


@pytest.mark.skip(reason="Not implemented")
def test_import_arcs():
    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    assert len(lines) == 8
    assert len(arcs) == 5

    import_arcs(arcs)
