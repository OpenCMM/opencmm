from server.mark.point import (
    get_shapes,
)
from server.mark import line, edge, arc
from server.config import MODEL_PATH, GCODE_PATH
from server import machine
from server.model import (
    update_offset,
)


def model_id_to_program_number(model_id: int):
    return str(model_id + 1000)
    # return str(model_id).zfill(4)


def program_number_to_model_id(program_number: str):
    try:
        return int(program_number) - 1000
    except ValueError:
        return None


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
    update_offset(model_id, offset)

    # save gcode
    program_number = model_id_to_program_number(model_id)
    gcode = edge.generate_gcode(path, program_number)
    gcode_filename = get_gcode_filename(stl_filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    edge.save_gcode(gcode, gcode_file_path)

    # send gcode to cnc machine
    machine_info = machine.get_machines(mysql_config)[0]
    machine.send_file_with_smbclient(machine_info, gcode_file_path)


def get_gcode_filename(model_filename: str):
    return f"{model_filename}.gcode"


def remove_data_with_model_id(model_id: int, mysql_config: dict):
    line.delete_sides_with_model_id(model_id, mysql_config)
    arc.delete_arcs_with_model_id(model_id, mysql_config)
    edge.delete_edges_with_model_id(model_id, mysql_config)
