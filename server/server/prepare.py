from cncmark.point import (
    get_shapes,
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    save_gcode,
)
from cncmark.line import import_lines
from cncmark.arc import import_arcs


def process_stl(
    mysql_config: dict,
    stl_file_path: str,
    measure_length: float,
    measure_feedrate: float,
    move_feedrate: float,
    offset: tuple,
):
    lines, arcs = get_shapes(stl_file_path)

    import_lines(lines, mysql_config)
    import_arcs(arcs, mysql_config)
    path = get_edge_path(
        mysql_config, measure_length, measure_feedrate, move_feedrate, offset
    )

    # save gcode
    gcode = generate_gcode(path)
    save_gcode(gcode, "data/gcode/opencmm.gcode")
