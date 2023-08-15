from cncmark.gcode import GCode
from cncmark.point import get_unique_points, get_shapes
import numpy as np


def test_gcode():
    points = np.array([[0, 10, 0], [0, 20, 0], [0, 30, 0]])
    gcode = GCode(points, 600)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 7
    assert gcode.gcode[1] == "G4 P1000"
    assert gcode.gcode[2] == "G1 X0 Y10 Z300.0 F600"
    assert gcode.gcode[3] == "G4 P1000"
    assert gcode.gcode[4] == "G1 X0 Y20 Z300.0 F600"
    assert gcode.gcode[5] == "G4 P1000"
    assert gcode.gcode[6] == "G1 X0 Y30 Z300.0 F600"

    for wait in gcode.camera_wait:
        assert wait == 2.0

    z = 10.0
    lines, arcs = get_shapes("tests/fixtures/stl/sample.stl", z)
    unique_points = get_unique_points(lines, arcs)
    gcode = GCode(unique_points, 600)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 47


def test_camera_wait():
    points = np.array([[0, 10, 0], [30, 10, 0], [30, 30, 0]])
    gcode = GCode(points, 600)
    gcode.generate_gcode()
    assert len(gcode.gcode) == 7
    assert gcode.camera_wait[0] == 2.0
    assert gcode.camera_wait[1] == 4.0
    assert gcode.camera_wait[2] == 3.0
