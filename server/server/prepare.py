from server.mark.point import (
    get_visible_facets,
    get_lines_on_coplanar_facets,
)
from server.mark.shape import Shape
from server.mark import line, edge, arc, pair, step, gcode, slope, trace
from server.mark.edge import EdgePath
from server.config import MODEL_PATH, GCODE_PATH
from server import machine
from server.model import (
    update_offset_gcode_settings,
)


def program_number_to_model_id(program_number: str):
    try:
        return int(program_number) - 1000
    except ValueError:
        return None


def process_new_3dmodel(stl_filename: str, model_id: int, mysql_config: dict):
    shape = Shape(f"{MODEL_PATH}/{stl_filename}")
    lines, arcs = shape.get_lines_and_arcs()
    if lines:
        for lines_on_coplanar_facets in lines:
            line.import_lines(model_id, lines_on_coplanar_facets, mysql_config)
        step.import_steps(mysql_config, model_id)
        slope.import_slopes(mysql_config, model_id)
    if arcs:
        for arcs_on_coplanar_facets in arcs:
            arc.import_arcs(model_id, arcs_on_coplanar_facets, mysql_config)


def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list


def process_new_model(stl_filename: str, model_id: int, mysql_config: dict):
    facets = get_visible_facets(f"{MODEL_PATH}/{stl_filename}")
    lines = get_lines_on_coplanar_facets(facets)
    line_pairs = flatten_extend(lines)
    line.import_lines_from_paired_lines_on_facets(model_id, line_pairs, mysql_config)
    step.import_steps(mysql_config, model_id)
    slope.import_slopes(mysql_config, model_id, lines)


def process_stl(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    gcode_settings: tuple,
    offset: tuple,
    send_gcode: bool,
):
    path = create_gcode_path(
        mysql_config,
        model_id,
        stl_filename,
        gcode_settings,
        offset,
    )
    # save gcode
    gcode_filename = gcode.get_gcode_filename(stl_filename)
    gcode_file_path = f"{GCODE_PATH}/{gcode_filename}"
    gcode.save_gcode(model_id, path, gcode_file_path)

    # send gcode to cnc machine
    if send_gcode:
        machine_info = machine.get_machines(mysql_config)[0]
        machine.send_file_with_smbclient(machine_info, gcode_file_path)


def create_gcode_path(
    mysql_config: dict,
    model_id: int,
    stl_filename: str,
    gcode_settings: tuple,
    offset: tuple,
    update_data: bool = True,
):
    (measurement_range, measure_feedrate, move_feedrate) = gcode_settings
    edge_path = EdgePath(
        mysql_config,
        model_id,
        stl_filename,
        gcode_settings,
    )
    path = edge_path.get_edge_path(offset, update_data)
    if update_data:
        update_offset_gcode_settings(model_id, offset, gcode_settings)

    path = gcode.format_edge_path(path)
    steps = step.get_steps(mysql_config, model_id)
    if steps:
        step_path, trace_lines = step.create_step_path(
            mysql_config,
            model_id,
            stl_filename,
            move_feedrate,
            offset,
        )

        # wait for 1 second in order to update the sensor config
        path.append("G4 P1000")
        init_line = 4 + len(path)
        trace_id = steps[0][0]
        if trace.get_trace_lines(mysql_config, trace_id) and update_data:
            trace_id_list = [step[0] for step in steps]
            trace.delete_trace_lines(mysql_config, trace_id_list)

        if update_data:
            trace.import_trace_lines(mysql_config, trace_lines, init_line)
        path += step_path

    slopes = slope.get_slopes(mysql_config, model_id)
    if slopes:
        slope_path, trace_lines = slope.create_slope_path(
            mysql_config,
            model_id,
            move_feedrate,
            offset,
        )

        if not steps:
            path.append("G4 P1000")
        init_line = 4 + len(path)
        trace_id = slopes[0][0]
        if trace.get_trace_lines(mysql_config, trace_id) and update_data:
            trace_id_list = [slope[0] for slope in slopes]
            trace.delete_trace_lines(mysql_config, trace_id_list)

        if update_data:
            trace.import_trace_lines(mysql_config, trace_lines, init_line)
        path += slope_path

    return path


def remove_data_with_model_id(model_id: int, mysql_config: dict):
    line.delete_sides_with_model_id(model_id, mysql_config)
    arc.delete_arcs_with_model_id(model_id, mysql_config)
    edge.delete_edges_with_model_id(model_id, mysql_config)
    pair.delete_row_with_model_id(model_id, mysql_config)
