from cncmark.point import (
    get_shapes,
)
from cncmark.edge import (
    get_edge_path,
    generate_gcode,
    save_gcode,
)
from cncmark import line
from cncmark import arc
from server.config import MODEL_PATH, GCODE_PATH
import mysql.connector


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
    path = get_edge_path(
        mysql_config, measure_length, measure_feedrate, move_feedrate, offset
    )

    # save gcode
    gcode = generate_gcode(path)
    save_gcode(gcode, f"{GCODE_PATH}/{stl_filename}.gcode")


def remove_data_with_model_id(model_id: int, mysql_config: dict):
    line.delete_row_with_model_id(model_id, mysql_config)
    arc.delete_row_with_model_id(model_id, mysql_config)
