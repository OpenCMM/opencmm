from server.measure.gcode import is_point_on_line, get_true_line_number, load_gcode

# from server.measure.mtconnect import get_mtconnect_data
# from server.config import MYSQL_CONFIG


def test_is_point_on_line():
    xy = (0.0, 0.0)
    start = (-1.0, -1.0)
    end = (1.0, 1.0)
    assert is_point_on_line(xy, start, end)


def test_is_point_on_line_round():
    xy = (27.529, -39.239)
    start = (28.147, -38.679)
    end = (24.443, -42.037)
    assert is_point_on_line(xy, start, end)
    assert not is_point_on_line(xy, start, end, 0.00000001)


def test_is_point_on_line_round_err():
    xy = (29.795, -12.838)
    start = (29.877, -14.503)
    end = (29.633, -9.509)
    assert is_point_on_line(xy, start, end, 1)
    assert not is_point_on_line(xy, start, end, 0.0000001)


def test_is_point_on_line_debug():
    xy = (33.333, -129.61)
    start = (33.333, -132.5)
    end = (33.333, -127.5)
    assert is_point_on_line(xy, start, end)
    # assert not is_point_on_line(xy, start, end, 0.0000001)

    xy = (33.333, -129.61)
    start = (33.333, -127.5)
    end = (33.333, 2.5)
    assert not is_point_on_line(xy, start, end)


def test_get_true_line_number_debug():
    gcode = load_gcode("data/gcode/sample.stl.gcode")
    xy = (33.333, -129.61)
    line = 29
    assert get_true_line_number(xy, line, gcode, None) == 28


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


# def test_is_point_on_line_from_mtconnect_data():
#     mtconnect_data = get_mtconnect_data(6, MYSQL_CONFIG)
#     gcode = load_gcode("data/gcode/demo.STL.gcode")
#     for row in mtconnect_data:
#         line = int(row[6])
#         xy = (row[3], row[4])
#         # if get_true_line_number(xy, line, gcode) is None:
#         #     breakpoint()

#         assert get_true_line_number(xy, line, gcode) == line
