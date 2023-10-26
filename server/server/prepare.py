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
from server.config import MODEL_PATH, GCODE_PATH


def process_stl(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    measure_config: tuple,
    offset: tuple,
):
    (measure_length, measure_feedrate, move_feedrate) = measure_config
    lines, arcs = get_shapes(f"{MODEL_PATH}/{stl_filename}")

    import_lines(model_id, lines, mysql_config)
    import_arcs(model_id, arcs, mysql_config)
    path = get_edge_path(
        mysql_config, measure_length, measure_feedrate, move_feedrate, offset
    )

    # save gcode
    gcode = generate_gcode(path)
    save_gcode(gcode, f"{GCODE_PATH}/{stl_filename}.gcode")
