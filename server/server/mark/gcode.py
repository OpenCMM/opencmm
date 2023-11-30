def to_gcode_row(x, y, feedrate):
    # round to 3 decimal places
    x = round(x, 3)
    y = round(y, 3)
    return f"G1 X{x} Y{y} F{feedrate}"


def model_id_to_program_number(model_id: int):
    return str(model_id + 1000)

    # return str(model_id).zfill(4)


def format_edge_path(edge_path: list):
    path = []
    for row in edge_path:
        path.append(row[0])
        path.append(row[1])
    return path


def generate_gcode(path, program_number: str):
    gcode = ["%", f"O{program_number}", "G90 G54"]
    for row in path:
        gcode.append(row)
    return gcode + ["M30", "%"]


def get_gcode_filename(model_filename: str):
    return f"{model_filename}.gcode"


def save_gcode(model_id: int, path, gcode_file_path: str):
    program_number = model_id_to_program_number(model_id)
    gcode = generate_gcode(path, program_number)
    with open(gcode_file_path, "w") as f:
        for line in gcode:
            f.write(line + "\n")
