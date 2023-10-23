import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from server.prepare import process_stl
from pydantic import BaseModel
from typing import Optional
from server import result
from listener.main import listener_start
from listener.status import get_process_status, start_measuring


class JobInfo(BaseModel):
    measure_length: float
    measure_feedrate: float
    move_feedrate: float
    x_offset: Optional[float] = 0.0
    y_offset: Optional[float] = 0.0
    z_offset: Optional[float] = 0.0
    z: Optional[float] = None


mysql_config = dict(
    host="192.168.122.230",
    port=3306,
    user="root",
    password="root",
)

model_path = "data/3dmodel/3dmodel.stl"

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

    with open(model_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"status": "ok"}


@app.get("/load/model/{model_id}")
async def load_model(model_id: str):
    return FileResponse(f"data/3dmodel/{model_id}.stl")


@app.get("/load/gcode/{filename}")
async def load_gcode(filename: str):
    return FileResponse(f"data/gcode/{filename}.gcode")


@app.post("/setup/data")
async def setup_data(job_info: JobInfo):
    """Find verticies, generate gcode"""

    # check if model exists
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="No model uploaded")
    offset = (job_info.x_offset, job_info.y_offset, job_info.z_offset)
    process_stl(
        mysql_config,
        model_path,
        job_info.measure_length,
        job_info.measure_feedrate,
        job_info.move_feedrate,
        offset,
        job_info.z,
    )

    return {"status": "ok"}


@app.get("/download/gcode")
async def download_gcode():
    """Download gcode file"""
    if not os.path.exists("data/gcode/opencmm.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    return FileResponse("data/gcode/opencmm.gcode")


@app.post("/start/measurement/{mtconnect_interval}")
async def start_measurement(mtconnect_interval: int, background_tasks: BackgroundTasks):
    sensor_ws_url = "ws://192.168.10.114:81"
    process_id = start_measuring(mysql_config, "running")
    background_tasks.add_task(
        listener_start, sensor_ws_url, mysql_config, mtconnect_interval, process_id
    )
    return {"status": "ok"}


@app.get("/load/image")
async def load_image():
    if not os.path.exists("data/images/result.png"):
        raise HTTPException(status_code=400, detail="No image file generated")
    return FileResponse("data/images/result.png")


@app.get("/result/edges")
async def get_result_edges():
    edges = result.fetch_edges()
    return {"edges": edges}


@app.get("/result/lines")
async def get_result_lines():
    lines = result.fetch_lines()
    return {"lines": lines}


@app.get("/result/arcs")
async def get_result_arcs():
    arcs = result.fetch_arcs()
    return {"arcs": arcs}


@app.get("/get_measurement_status/{process_id}")
async def get_measurement_status(process_id: int):
    return get_process_status(mysql_config, process_id)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
