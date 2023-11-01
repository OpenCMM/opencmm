import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from server.prepare import process_stl
from pydantic import BaseModel
from typing import Optional
from server import result
from listener.main import listener_start
from listener.status import get_process_status, start_measuring, get_running_process
from listener.hakaru import ping_sensor
from server.coord import get_final_coordinates
from server.config import MYSQL_CONFIG, MODEL_PATH, SENSOR_IP
from server.model import (
    get_3dmodel_data,
    get_recent_3dmodel_data,
    get_3dmodel_file_info,
    model_exists,
    model_id_to_filename,
    add_new_3dmodel,
)
import asyncio


class JobInfo(BaseModel):
    three_d_model_id: int
    measure_length: float
    measure_feedrate: float
    move_feedrate: float
    x_offset: Optional[float] = 0.0
    y_offset: Optional[float] = 0.0
    z_offset: Optional[float] = 0.0


class MeasurementConfig(BaseModel):
    three_d_model_id: int
    mtconnect_interval: int
    interval: int
    threshold: int


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
]


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

    return {"status": "ok", "model_id": _model_id}


@app.get("/list/3dmodels")
async def list_3dmodels():
    """List uploaded 3d models"""
    return {"models": get_3dmodel_data()}


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
    )

    return {"status": "ok"}


@app.get("/download/gcode/{model_id}")
async def download_gcode(model_id: int):
    """Download gcode file"""
    filename = model_id_to_filename(model_id)
    if not os.path.exists(f"data/gcode/{filename}.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    return FileResponse(f"data/gcode/{filename}.gcode")


@app.post("/start/measurement")
async def start_measurement(
    _conf: MeasurementConfig, background_tasks: BackgroundTasks
):
    sensor_ws_url = f"ws://{SENSOR_IP}:81"
    # sensor_ws_url = "ws://192.168.0.35:81"
    # mtconnect_url = (
    #     "http://192.168.0.19:5000/current?path=//Axes/Components/Linear/DataItems"
    # )
    mtconnect_url = "https://demo.metalogi.io/current?path=//Axes/Components/Linear/DataItems/DataItem"
    # sensor_ws_url = "ws://localhost:8081"

    running_process = get_running_process(_conf.three_d_model_id, MYSQL_CONFIG)
    if running_process is not None:
        raise HTTPException(
            status_code=400,
            detail="Measurement already running (process id: {running_process[0]}))",
        )

    filename = model_id_to_filename(_conf.three_d_model_id)
    final_coordinates = get_final_coordinates(f"data/gcode/{filename}.gcode")
    process_id = start_measuring(_conf.three_d_model_id, MYSQL_CONFIG, "running")
    background_tasks.add_task(
        listener_start,
        sensor_ws_url,
        MYSQL_CONFIG,
        (mtconnect_url, _conf.mtconnect_interval),
        process_id,
        _conf.three_d_model_id,
        final_coordinates,
        (_conf.interval, _conf.threshold),
    )
    return {"status": "ok"}


@app.get("/get_sensor_status/{model_id}")
async def get_sensor_status(model_id: int):
    if not ping_sensor(SENSOR_IP):
        return {"status": "sensor not found or turned off", "data": None}
    running_process = get_running_process(model_id, MYSQL_CONFIG)
    if running_process is None:
        return {"status": "process not found", "data": None}
    return {"status": "ok", "data": running_process}


@app.websocket("/ws/{model_id}")
async def websocket_endpoint(model_id: int, websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            _process_data = await get_sensor_status(model_id)
            if _process_data["status"] == "ok":
                status = {
                    "process_id": _process_data["data"][0],
                    "status": _process_data["data"][2],
                    "error": _process_data["data"][3],
                }
            else:
                status = {
                    "process_id": -1,
                    "status": _process_data["status"],
                    "error": "",
                }
            await websocket.send_json(status)
            await asyncio.sleep(1)
    except ConnectionClosedOK or ConnectionClosedError:
        await websocket.close()


@app.get("/result/edges/{model_id}")
async def get_result_edges(model_id: int):
    edges = result.fetch_edges(model_id)
    return {"edges": edges}


@app.get("/result/lines/{model_id}")
async def get_result_lines(model_id: int):
    lines = result.fetch_lines(model_id)
    return {"lines": lines}

@app.get("/result/pairs/{model_id}")
async def get_result_pair(model_id: int):
    pairs = result.fetch_pairs(model_id)
    return {"pairs": pairs}


@app.get("/result/arcs/{model_id}")
async def get_result_arcs(model_id: int):
    arcs = result.fetch_arcs(model_id)
    return {"arcs": arcs}


@app.get("/get_measurement_status/{process_id}")
async def get_measurement_status(process_id: int):
    return get_process_status(MYSQL_CONFIG, process_id)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
