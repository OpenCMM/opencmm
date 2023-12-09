from server.measure.sensor import sensor_output_diff_to_mm


def test_sensor_output_diff_to_mm():
    assert sensor_output_diff_to_mm(0) == 0.0
    assert sensor_output_diff_to_mm(-798.0) == -3.02
