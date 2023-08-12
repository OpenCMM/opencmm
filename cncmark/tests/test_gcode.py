from cncmark.gcode import GCode
from cncmark.point import get_unique_points, get_lines
import numpy as np


def test_gcode():
    points = np.array([[0, 10, 0], [0, 20, 0], [0, 30, 0]])
    gcode = GCode(points, 600)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 6
    assert gcode.gcode[0] == "G4 P1"
    assert gcode.gcode[1] == "G1 X0 Y10 Z0 F600"
    assert gcode.gcode[2] == "G4 P1"
    assert gcode.gcode[3] == "G1 X0 Y20 Z0 F600"
    assert gcode.gcode[4] == "G4 P1"
    assert gcode.gcode[5] == "G1 X0 Y30 Z0 F600"

    for wait in gcode.pic_wait:
        assert wait == 2.0

    z = 10.0
    lines = get_lines("tests/fixtures/stl/sample.stl", z)
    unique_points = get_unique_points(lines)
    gcode = GCode(unique_points)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 24


def test_pic_wait():
    points = np.array([[0, 10, 0], [30, 10, 0], [30, 30, 0]])
    gcode = GCode(points, 600)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 6
    assert gcode.pic_wait[0] == 2.0
    assert gcode.pic_wait[1] == 4.0
    assert gcode.pic_wait[2] == 3.0