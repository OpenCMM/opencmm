def to_gcode_row(x, y, feedrate):
    # round to 3 decimal places
    x = round(x, 3)
    y = round(y, 3)
    return f"G1 X{x} Y{y} F{feedrate}"
