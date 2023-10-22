from cncmark.point import (
    get_shapes,
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    import_edges_from_sides,
    save_gcode,
)
from cncmark.line import import_parallel_lines, get_sides
from typing import Optional


def process_stl(
    stl_file_path: str,
    measure_length: float,
    measure_feedrate: float,
    move_feedrate: float,
    offset: tuple,
    z: Optional[float],
):
    z = 10.0
    lines, arcs = get_shapes(stl_file_path, z)

    import_parallel_lines(lines)
    sides = get_sides()
    import_edges_from_sides(sides)
    path = get_edge_path(sides, measure_length, measure_feedrate, move_feedrate, offset)

    # save gcode
    gcode = generate_gcode(path)
    save_gcode(gcode, "data/gcode/opencmm.gcode")
