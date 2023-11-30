from server.mark.point import (
    get_shapes,
    get_visible_facets,
    get_lines_on_coplanar_facets,
)
from server.mark import line, edge, arc, pair, step, gcode
from server.config import MODEL_PATH, GCODE_PATH
from server import machine
from server.model import (
    update_offset,
)


def program_number_to_model_id(program_number: str):
    try:
        return int(program_number) - 1000
    except ValueError:
        return None


def process_new_3dmodel(stl_filename: str, model_id: int, mysql_config: dict):
    lines, arcs = get_shapes(f"{MODEL_PATH}/{stl_filename}")
    line.import_lines(model_id, lines, mysql_config)
    arc.import_arcs(model_id, arcs, mysql_config)


def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list


def process_new_model(stl_filename: str, model_id: int, mysql_config: dict):
    facets = get_visible_facets(f"{MODEL_PATH}/{stl_filename}")
    lines = get_lines_on_coplanar_facets(facets)
    lines = flatten_extend(lines)
    line.import_lines_from_paired_lines_on_facets(model_id, lines, mysql_config)
    step.import_steps(model_id, mysql_config)


def process_stl(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    measure_config: tuple,
    offset: tuple,
    send_gcode: bool,
):
    (measure_length, measure_feedrate, move_feedrate) = measure_config
    path = edge.get_edge_path(
        mysql_config,
        model_id,
        stl_filename,
        measure_length,
        measure_feedrate,
        move_feedrate,
        offset,
    )
    update_offset(model_id, offset)

    # add line numbers
    edge.add_line_number_from_path(mysql_config, path)

    # save gcode
    gcode_filename = gcode.get_gcode_filename(stl_filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode.save_gcode(model_id, path, stl_filename)

    # send gcode to cnc machine
    if send_gcode:
        machine_info = machine.get_machines(mysql_config)[0]
        machine.send_file_with_smbclient(machine_info, gcode_file_path)


def remove_data_with_model_id(model_id: int, mysql_config: dict):
    line.delete_sides_with_model_id(model_id, mysql_config)
    arc.delete_arcs_with_model_id(model_id, mysql_config)
    edge.delete_edges_with_model_id(model_id, mysql_config)
    pair.delete_row_with_model_id(model_id, mysql_config)
