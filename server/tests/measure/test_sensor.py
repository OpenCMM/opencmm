from server.measure.sensor import (
    sensor_output_diff_to_mm,
    mm_to_sensor_output,
    mm_to_sensor_output_diff,
)


def test_sensor_output_diff_to_mm():
    assert sensor_output_diff_to_mm(0) == 0.0
    assert sensor_output_diff_to_mm(-798.0) == -3.02


def test_mm_to_sensor_output():
    assert mm_to_sensor_output(0) == 9400.0
    # first = mm_to_sensor_output(-7.2)
    # second = mm_to_sensor_output(-4.69)
    # third = mm_to_sensor_output(-2.22)


def test_mm_to_sensor_output_diff():
    assert mm_to_sensor_output_diff(-3.02) == -798.0
    assert mm_to_sensor_output_diff(3.02) == 798.0
    assert int(mm_to_sensor_output_diff(3.022)) == 798
