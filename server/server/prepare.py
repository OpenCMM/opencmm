from cncmark.point import get_shapes, get_unique_points, import_points
from cncmark.line import import_lines
from .arc import import_arcs
from cncmark.gcode import GCode


def process_stl(stl_file_path: str, z: float, camera_height: float, feed_rate: float):
    z = 10.0
    lines, arcs = get_shapes(stl_file_path, z)
    import_lines(lines)
    import_arcs(arcs)
    unique_points = get_unique_points(lines, arcs)
    import_points(unique_points)

    # save gcode
    gcode = GCode(unique_points, feed_rate, camera_height)
    gcode.generate_gcode()
    gcode.save_gcode("data/gcode/opencmm.gcode")
    camera_wait = gcode.camera_wait
    # save camera_wait list to file
    with open("data/gcode/camera_wait.txt", "w") as f:
        for i, wait in enumerate(camera_wait):
            x = unique_points[i][0]
            y = unique_points[i][1]
            z = unique_points[i][2]
            f.write(f"{x} {y} {z} {str(wait)}\n")
