from cncmark.point import get_lines, import_lines, get_unique_points, import_points
from cncmark.gcode import GCode

def process_stl(stl_file_path: str, z: float, camera_height: float, feed_rate: float):
    z = 10.0
    lines = get_lines(stl_file_path, z)
    import_lines(lines)
    unique_points = get_unique_points(lines)
    import_points(unique_points)

    # save gcode
    gcode = GCode(unique_points, feed_rate, camera_height)
    gcode.generate_gcode()
    gcode.save_gcode("data/gcode/opencmm.gcode")
    pic_wait = gcode.pic_wait
    # save pic_wait list to file
    with open("data/gcode/pic_wait.txt", "w") as f:
        for wait in pic_wait:
            f.write(str(wait) + "\n")

