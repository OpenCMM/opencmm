from cncmark.gcode import get_gcode
from cncmark.point import get_unique_points, get_lines


def test_get_gcode():
    points = [[0, 0, 0], [0, 0, 1], [0, 0, 2]]
    gcode = get_gcode(points)
    assert len(gcode) == 3
    assert gcode[0] == "G1 X0 Y0 Z0"
    assert gcode[1] == "G1 X0 Y0 Z1"
    assert gcode[2] == "G1 X0 Y0 Z2"

    z = 10.0
    lines = get_lines("tests/fixtures/stl/sample.stl", z)
    unique_points = get_unique_points(lines)
    gcode = get_gcode(unique_points)
    assert len(gcode) == 12
