from server.type.sensor import SensorConfig
from server.type.mtconnect import MTConnectConfig
from server.type.measurement import (
    EdgeDetectionConfig,
    MeasurementConfig,
    MeasurementConfigWithProgram,
    TraceConfig,
)
import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from server.prepare import (
    process_new_3dmodel,
    process_new_model,
    process_stl,
    program_number_to_model_id,
)
from pydantic import BaseModel
from typing import Optional
from server import result
from server.listener import (
    listener_start,
    status,
    hakaru,
)
from server.measure import EstimateConfig, update_data_after_measurement, recompute
from server.measure.mtconnect import (
    check_if_mtconnect_data_is_missing,
    MtctDataChecker,
    update_mtct_latency,
)
from server.measure.gcode import get_gcode_line_path
from server.config import MYSQL_CONFIG, MODEL_PATH, get_config, update_conf
from server.model import (
    get_3dmodel_data,
    get_recent_3dmodel_data,
    get_model_shapes,
    get_3dmodel_file_info,
    model_exists,
    list_3dmodel,
    model_id_to_filename,
    add_new_3dmodel,
    get_model_data,
    delete_model_files,
)
from server.mark.gcode import model_id_to_program_number, get_gcode_filename
from server import machine
from server.mark.trace import get_first_line_number_for_tracing
import asyncio


class JobInfo(BaseModel):
    three_d_model_id: int
    measurement_range: float
    measure_feedrate: float
    move_feedrate: float
    x_offset: Optional[float] = 0.0
    y_offset: Optional[float] = 0.0
    z_offset: Optional[float] = 0.0
    send_gcode: Optional[bool] = True


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}


@app.get("/mtconnect_url")
def get_mtconnect_url():
    conf = get_config()
    return {"url": conf["mtconnect"]["url"]}


@app.post("/update/mtconnect_url")
def update_mtconnect_url(url: str):
    conf = get_config()
    conf["mtconnect"]["url"] = url
    update_conf(conf)
    return {"status": "ok"}


@app.get("/get/mtconnect_config")
def get_mtconnect_config():
    conf = get_config()["mtconnect"]
    return {
        "url": conf["url"],
        "interval": conf["interval"],
        "latency": conf["latency"],
    }


@app.post("/update/mtconnect_config")
def update_mtconnect_config(_conf: MTConnectConfig):
    conf = get_config()
    conf["mtconnect"]["url"] = _conf.url
    conf["mtconnect"]["interval"] = _conf.interval
    conf["mtconnect"]["latency"] = _conf.latency
    update_conf(conf)
    return {"status": "ok"}


@app.get("/get/sensor_config")
def get_sensor_config():
    conf = get_config()["sensor"]
    return {
        "interval": conf["interval"],
        "threshold": conf["threshold"],
        "beam_diameter": conf["beam_diameter"],
        "middle_output": conf["middle_output"],
        "response_time": conf["response_time"],
        "tolerance": conf["tolerance"],
    }


@app.post("/update/sensor_config")
def update_sensor_config(_conf: SensorConfig):
    conf = get_config()
    conf["sensor"]["interval"] = _conf.interval
    conf["sensor"]["threshold"] = _conf.threshold
    conf["sensor"]["beam_diameter"] = _conf.beam_diameter
    conf["sensor"]["middle_output"] = _conf.middle_output
    conf["sensor"]["response_time"] = _conf.response_time
    conf["sensor"]["tolerance"] = _conf.tolerance
    update_conf(conf)
    return {"status": "ok"}


@app.get("/get/edge_detection_config")
def get_edge_detection_config():
    conf = get_config()["edge"]
    return {
        "arc_number": conf["arc"]["number"],
        "line_number": conf["line"]["number"],
    }


@app.post("/update/edge_detection_config")
def update_edge_detection_config(_conf: EdgeDetectionConfig):
    conf = get_config()
    conf["edge"]["arc"]["number"] = _conf.arc_number
    conf["edge"]["line"]["number"] = _conf.line_number
    update_conf(conf)
    return {"status": "ok"}


@app.get("/get/trace_config")
def get_trace_config():
    conf = get_config()["trace"]
    return {
        "min_measure_count": conf["min_measure_count"],
        "max_feedrate": conf["max_feedrate"],
        "interval": conf["interval"],
        "margin": conf["margin"],
        "slope_number": conf["slope"]["number"],
    }


@app.post("/update/trace_config")
def update_trace_config(_conf: TraceConfig):
    conf = get_config()
    conf["trace"]["min_measure_count"] = _conf.min_measure_count
    conf["trace"]["max_feedrate"] = _conf.max_feedrate
    conf["trace"]["interval"] = _conf.interval
    conf["trace"]["margin"] = _conf.margin
    conf["trace"]["slope"]["number"] = _conf.slope_number
    update_conf(conf)
    return {"status": "ok"}


@app.post("/upload/3dmodel")
async def upload_3dmodel(file: UploadFile):
    """Upload 3d model file"""
    # save image
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ["stl", "STL"]:
        raise HTTPException(status_code=400, detail="File extension not supported")

    _model_id = add_new_3dmodel(file.filename)
    with open(f"{MODEL_PATH}/{file.filename}", "wb") as buffer:
        buffer.write(await file.read())
    process_new_3dmodel(file.filename, _model_id, MYSQL_CONFIG)
    return {"status": "ok", "model_id": _model_id}


@app.post("/upload/new/model")
async def upload_new_model(file: UploadFile):
    """Upload new 3d model file"""
    # save image
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ["stl", "STL"]:
        raise HTTPException(status_code=400, detail="File extension not supported")

    _model_id = add_new_3dmodel(file.filename)
    with open(f"{MODEL_PATH}/{file.filename}", "wb") as buffer:
        buffer.write(await file.read())
    process_new_model(file.filename, _model_id, MYSQL_CONFIG)
    return {"status": "ok", "model_id": _model_id}


@app.delete("/delete/model")
async def delete_model_data(model_id: int):
    """Delete model data"""
    delete_model_files(model_id)
    return {"status": "ok"}


@app.get("/list/3dmodels")
async def list_3dmodels():
    """List uploaded 3d models"""
    return {"models": get_3dmodel_data()}


@app.get("/list/all/3dmodels")
async def list_all_3dmodels():
    """List all uploaded 3d models"""
    return {"models": list_3dmodel()}


@app.get("/list/recent/3dmodels")
async def list_recent_3dmodels(limit: int = 5):
    """List recently used 3d models"""
    return {"models": get_recent_3dmodel_data(limit)}


@app.get("/get/3dmodel/info/{model_id}")
async def get_3dmodel_info(model_id: int):
    """Get 3d model info"""
    return get_3dmodel_file_info(model_id)


@app.get("/load/model/{model_id}")
async def load_model(model_id: str):
    model_id = int(model_id)
    filename = model_id_to_filename(model_id)
    return FileResponse(f"data/3dmodel/{filename}")


@app.get("/load/gcode/{model_id}")
async def load_gcode(model_id: str):
    model_id = int(model_id)
    filename = model_id_to_filename(model_id)
    return FileResponse(f"data/gcode/{filename}.gcode")


@app.post("/setup/data")
async def setup_data(job_info: JobInfo):
    """Find verticies, generate gcode"""

    filename = model_id_to_filename(job_info.three_d_model_id)
    if not model_exists(filename):
        raise HTTPException(status_code=400, detail="No model uploaded")
    offset = (job_info.x_offset, job_info.y_offset, job_info.z_offset)
    gcode_settings = (
        job_info.measurement_range,
        job_info.measure_feedrate,
        job_info.move_feedrate,
    )
    process_stl(
        MYSQL_CONFIG,
        job_info.three_d_model_id,
        filename,
        gcode_settings,
        offset,
        job_info.send_gcode,
    )

    return {"status": "ok"}


@app.get("/get/gcode/info/{model_id}")
async def get_gcode_info(model_id: int):
    """Get gcode info"""
    filename = model_id_to_filename(model_id)
    if not os.path.exists(f"data/gcode/{filename}.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    gcode_filename = get_gcode_filename(filename)
    program_number = model_id_to_program_number(model_id)
    return {
        "filename": gcode_filename,
        "program_number": program_number,
    }


@app.get("/download/gcode/{model_id}")
async def download_gcode(model_id: int):
    """Download gcode file"""
    filename = model_id_to_filename(model_id)
    if not os.path.exists(f"data/gcode/{filename}.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    return FileResponse(
        f"data/gcode/{filename}.gcode", media_type="blob", filename=f"{filename}.gcode"
    )


@app.get("/gcode/lines/{model_id}")
async def get_gcode_lines(model_id: int):
    filename = model_id_to_filename(model_id)
    gcode_filepath = f"data/gcode/{filename}.gcode"
    if not os.path.exists(gcode_filepath):
        raise HTTPException(status_code=400, detail="No gcode file generated")

    return {"lines": get_gcode_line_path(gcode_filepath)}


@app.post("/start/measurement")
async def start_measurement(
    _conf: MeasurementConfig, background_tasks: BackgroundTasks
):
    model_id = _conf.three_d_model_id
    running_process = status.get_running_process(model_id, MYSQL_CONFIG)
    if running_process is not None:
        raise HTTPException(
            status_code=400,
            detail="Measurement already running",
        )

    tracing_start_line = get_first_line_number_for_tracing(MYSQL_CONFIG, model_id)
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    if process_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid model_id",
        )
    background_tasks.add_task(
        listener_start,
        MYSQL_CONFIG,
        process_id,
    )
    return {"status": "ok", "tracing_start_line": tracing_start_line}


@app.post("/start/measurement/with/program_name")
async def start_measurement_with_program_name(
    _conf: MeasurementConfigWithProgram, background_tasks: BackgroundTasks
):
    model_id = program_number_to_model_id(_conf.program_name)
    if model_id is None:
        return {"status": "Not a CMM program", "model_id": None}
    model_row = get_model_data(model_id)
    if model_row is None:
        return {"status": "Not a CMM program", "model_id": None}
    model_id = model_row[0]
    running_process = status.get_running_process(model_id, MYSQL_CONFIG)
    if running_process is not None:
        raise HTTPException(
            status_code=400,
            detail="Measurement already running",
        )

    tracing_start_line = get_first_line_number_for_tracing(MYSQL_CONFIG, model_id)
    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    if process_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid model_id",
        )
    background_tasks.add_task(
        listener_start,
        MYSQL_CONFIG,
        process_id,
    )
    return {
        "status": "ok",
        "model_id": model_id,
        "tracing_start_line": tracing_start_line,
    }


@app.post("/estimate/measurement")
async def estimate_measurement(
    _conf: EstimateConfig, background_tasks: BackgroundTasks
):
    _process = status.get_process_status(MYSQL_CONFIG, _conf.process_id)
    if _process is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid process_id",
        )

    # add process status check

    model_id = _process[1]
    background_tasks.add_task(
        update_data_after_measurement,
        MYSQL_CONFIG,
        _conf.process_id,
        model_id,
    )
    return {"status": "ok", "process_id": _conf.process_id}


@app.post("/recompute/process/{process_id}")
async def recompute_process(process_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        recompute,
        MYSQL_CONFIG,
        process_id,
    )
    return {"status": "ok"}


@app.get("/get_model_id/from/program_name/{program_name}")
async def get_model_id_from_program_name(program_name: str):
    model_id = program_number_to_model_id(program_name)
    if model_id is None:
        return {"model_id": None}
    if get_model_data(model_id) is None:
        return {"model_id": None}
    return {"model_id": model_id}


@app.get("/get_sensor_status")
async def get_sensor_status():
    if not hakaru.ping_sensor():
        return {"status": "off"}
    return {"status": "on"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            _sensor_status = await get_sensor_status()
            await websocket.send_json(_sensor_status)
            await asyncio.sleep(1)
    except ConnectionClosedOK or ConnectionClosedError or KeyboardInterrupt:
        await websocket.close()


@app.get("/result/edges/{model_id}")
async def get_result_edges(model_id: int):
    edges = result.fetch_edges(model_id)
    return {"edges": edges}


@app.get("/result/edges/result/{process_id}")
async def get_edge_result(process_id: int):
    edges = result.fetch_edge_result(process_id)
    return {"edges": edges}


@app.get("/result/edges/result/combined/{model_id}/{process_id}")
async def get_edge_result_combined(model_id: int, process_id: int):
    edges = result.fetch_edge_result_combined(model_id, process_id)
    return {"edges": edges}


@app.get("/result/debug/points/{process_id}")
def get_debug_points(process_id: int):
    points = result.fetch_unique_points(process_id)
    return {"points": points}


@app.get("/result/debug/mtconnect/points/{process_id}")
def get_debug_mtconnect_points(process_id: int):
    points = result.fetch_mtconnect_points(process_id)
    return {"points": points}


@app.get("/result/check/mtconnect/points/{model_id}/{process_id}")
def check_mtconnect_points(model_id: int, process_id: int):
    lines = check_if_mtconnect_data_is_missing(MYSQL_CONFIG, model_id, process_id)
    return {"lines": lines}


@app.get("/get/model/table/data/{model_id}")
def get_model_table_data(model_id: int):
    return get_model_data(model_id)


@app.get("/result/lines")
async def get_result_lines(model_id: int, process_id: int):
    lines = result.fetch_lines(model_id, process_id)
    return {"lines": lines}


@app.get("/result/pairs/{model_id}")
async def get_result_pair(model_id: int):
    pairs = result.fetch_pairs(model_id)
    return {"pairs": pairs}


@app.get("/result/arcs")
async def get_result_arcs(model_id: int, process_id: int):
    arcs = result.fetch_arcs(model_id, process_id)
    return {"arcs": arcs}


@app.get("/result/steps")
async def get_result_steps(model_id: int, process_id: int):
    steps = result.fetch_step_results(model_id, process_id)
    return {"steps": steps}


@app.get("/result/slopes")
async def get_result_slopes(model_id: int, process_id: int):
    slopes = result.fetch_slope_results(model_id, process_id)
    return {"slopes": slopes}


@app.get("/result/mtconnect/lines")
async def get_timestamps_on_lines(model_id: int, process_id: int):
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, model_id, process_id)
    lines = mtct_data_checker.estimate_timestamps_from_mtct_data()
    return {"lines": lines.tolist()}


@app.get("/result/mtconnect/avg/delay")
async def get_mtct_delay_between_lines(model_id: int, process_id: int):
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, model_id, process_id)
    avg, delays = mtct_data_checker.get_average_delay_between_lines()
    return {"avg": avg, "delay": delays.tolist()}


@app.get("/result/mtconnect/missing/lines/travel/time/diff")
async def get_missing_lines_travel_time_diff(model_id: int, process_id: int):
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, model_id, process_id)
    avg, np_diff = mtct_data_checker.missing_line_travel_time_diff()
    if avg is None:
        return {"avg": None, "diff": []}
    return {"avg": avg, "diff": np_diff.tolist()}


@app.get("/model/shapes/{model_id}")
async def get_model_shape_data(model_id: int):
    lines, arcs = get_model_shapes(model_id)
    return {"lines": lines, "arcs": arcs}


@app.get("/sensor/positions/{model_id}/{process_id}")
async def get_sensor_positions(
    model_id: int, process_id: int, mtct_latency: float = None
):
    mtct_data_checker = MtctDataChecker(MYSQL_CONFIG, model_id, process_id)
    sensor_positions, mtct_latency = mtct_data_checker.get_sensor_data_with_coordinates(
        mtct_latency
    )
    return {"sensor": sensor_positions, "latency": mtct_latency}


@app.post("/update/mtconnect/latency/{process_id}")
async def update_mtconnect_latency(process_id: int, mtct_latency: float):
    update_mtct_latency(MYSQL_CONFIG, process_id, mtct_latency)
    return {"status": "ok"}


@app.get("/list/processes/{model_id}")
async def get_process_list(model_id: int):
    processes = status.get_process_list(MYSQL_CONFIG, model_id)
    return {"processes": processes}


@app.get("/get/prev/next/processes/{model_id}/{process_id}")
async def fetch_next_prev_process(model_id: int, process_id: int):
    prev, next = status.get_prev_next_process(MYSQL_CONFIG, model_id, process_id)
    return {"prev": prev, "next": next}


@app.get("/get_process_info/{process_id}")
async def fetch_process_info(process_id: int):
    return status.get_process_info(MYSQL_CONFIG, process_id)


@app.get("/get_first_machine")
def get_first_machine():
    machines = machine.get_machines(MYSQL_CONFIG)
    if len(machines) == 0:
        first_machine = (1, "192.168.0.1", "username", "password", "share_folder")
        machine.insert_machine(MYSQL_CONFIG, machine.MachineInfo(*first_machine))
        return first_machine
    return machines[0]


@app.post("/update_machine")
def update_machine(machine_info: machine.MachineInfo):
    machine.update_machine(MYSQL_CONFIG, machine_info)
    return {"status": "ok"}


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)
