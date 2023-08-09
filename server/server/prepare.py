from cncmark.point import get_lines, import_lines, get_unique_points, import_points
from cncmark.gcode import get_gcode, save_gcode

def process_stl(stl_file_path: str, z: float):
    z = 10.0
    lines = get_lines(stl_file_path, z)
    import_lines(lines)
    unique_points = get_unique_points(lines)
    import_points(unique_points)

    # save gcode
    gcode = get_gcode(unique_points)
    save_gcode(gcode, "data/gcode/opencmm.gcode")