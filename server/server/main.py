from server.type.mtconnect import MTConnectConfig
from server.type.measurement import MeasurementConfig, MeasurementConfigWithProgram
import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from server.prepare import (
    process_new_3dmodel,
    process_stl,
    get_gcode_filename,
    model_id_to_program_number,
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
from server.measure import EstimateConfig, update_data_after_measurement
from server.config import MYSQL_CONFIG, MODEL_PATH, get_config, update_conf
from server.model import (
    get_3dmodel_data,
    get_recent_3dmodel_data,
    get_3dmodel_file_info,
    model_exists,
    list_3dmodel,
    model_id_to_filename,
    add_new_3dmodel,
    get_model_data,
)
from server import machine
import asyncio


class JobInfo(BaseModel):
    three_d_model_id: int
    measure_length: float
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
    process_stl(
        MYSQL_CONFIG,
        job_info.three_d_model_id,
        filename,
        (job_info.measure_length, job_info.measure_feedrate, job_info.move_feedrate),
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


@app.post("/start/measurement")
async def start_measurement(
    _conf: MeasurementConfig, background_tasks: BackgroundTasks
):
    running_process = status.get_running_process(_conf.three_d_model_id, MYSQL_CONFIG)
    if running_process is not None:
        raise HTTPException(
            status_code=400,
            detail="Measurement already running",
        )

    process_id = status.start_measuring(_conf.three_d_model_id, MYSQL_CONFIG, "running")
    background_tasks.add_task(
        listener_start,
        MYSQL_CONFIG,
        _conf.mtconnect_interval,
        process_id,
        (_conf.interval, _conf.threshold),
    )
    return {"status": "ok"}


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

    process_id = status.start_measuring(model_id, MYSQL_CONFIG, "running")
    background_tasks.add_task(
        listener_start,
        MYSQL_CONFIG,
        _conf.mtconnect_interval,
        process_id,
        (_conf.interval, _conf.threshold),
    )
    return {"status": "ok", "model_id": model_id}


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


@app.get("/list/processes/{model_id}")
async def get_process_list(model_id: int):
    processes = status.get_process_list(MYSQL_CONFIG, model_id)
    return {"processes": processes}


@app.get("/get/prev/next/processes/{model_id}/{process_id}")
async def fetch_next_prev_process(model_id: int, process_id: int):
    prev, next = status.get_prev_next_process(MYSQL_CONFIG, model_id, process_id)
    return {"prev": prev, "next": next}


@app.get("/get_measurement_status/{process_id}")
async def get_measurement_status(process_id: int):
    return status.get_process_status(MYSQL_CONFIG, process_id)


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
