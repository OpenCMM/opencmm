def get_field_of_view(focal_length: float, sensor_width: float, distance: float):
    return sensor_width / focal_length * distance


def get_pixel_per_mm(field_of_view: float, pixel_width: int):
    return pixel_width / field_of_view
