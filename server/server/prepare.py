from cncmark.point import (
	get_shapes,
    get_sides
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    import_edges_from_sides,
    save_gcode,
)
from cncmark.line import import_lines, import_parallel_lines
from .arc import import_arcs
from typing import Optional


def process_stl(
    stl_file_path: str,
    measure_length: float,
    measure_feedrate: float,
    move_feedrate: float,
    offset,
    z: Optional[float],
):
    z = 10.0
    lines, arcs = get_shapes(stl_file_path, z)
    import_lines(lines)
    import_arcs(arcs)

    import_parallel_lines(lines)
    sides = get_sides()
    import_edges_from_sides(sides)
    path = get_edge_path(sides, measure_length, measure_feedrate, move_feedrate)


    # save gcode
    gcode = generate_gcode(path)
    save_gcode(gcode, "data/gcode/opencmm.gcode")