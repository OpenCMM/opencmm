from server.measure.gcode import is_point_on_line, get_true_line_number, load_gcode


def test_is_point_on_line():
    xy = (0.0, 0.0)
    start = (-1.0, -1.0)
    end = (1.0, 1.0)
    assert is_point_on_line(xy, start, end) is True


def test_get_true_line_number():
    gcode = load_gcode("data/gcode/sample.stl.gcode")
    xy = (10.289, -56.699)
    line = 4
    assert get_true_line_number(xy, line, gcode) is None

    xy = (0.209, -86.667)
    line = 6
    assert get_true_line_number(xy, line, gcode) == 4

    xy = (-2.164, -46.243)
    line = 7
    assert get_true_line_number(xy, line, gcode) == 5

    xy = (1.668, -43.333)
    line = 8
    assert get_true_line_number(xy, line, gcode) == 6
