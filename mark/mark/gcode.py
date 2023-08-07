def get_gcode(points):
    gcode = []
    for point in points:
        gcode.append(f"G1 X{point[0]} Y{point[1]} Z{point[2]}")
    return gcode


def save_gcode(gcode, file_path: str):
    with open(file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")
