from cncmark.point import (
    get_shapes,
)
from cncmark import line, edge, arc
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

    remove_data_with_model_id(model_id, mysql_config)
    line.import_lines(model_id, lines, mysql_config)
    arc.import_arcs(model_id, arcs, mysql_config)
    path = edge.get_edge_path(
        mysql_config, model_id, measure_length, measure_feedrate, move_feedrate, offset
    )

    # save gcode
    gcode = edge.generate_gcode(path, model_id)
    edge.save_gcode(gcode, f"{GCODE_PATH}/{stl_filename}.gcode")


def remove_data_with_model_id(model_id: int, mysql_config: dict):
    line.delete_sides_with_model_id(model_id, mysql_config)
    arc.delete_arcs_with_model_id(model_id, mysql_config)
    edge.delete_edges_with_model_id(model_id, mysql_config)
