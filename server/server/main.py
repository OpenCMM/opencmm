import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from server.prepare import process_stl
from pydantic import BaseModel
from server.reset import reset_tables
from typing import Optional
from server.result import fetch_points, fetch_arcs, fetch_lines


class JobInfo(BaseModel):
    measure_length: float
    measure_feedrate: float
    move_feedrate: float
    x_offset: Optional[float]
    y_offset: Optional[float]
    z_offset: Optional[float]
    z: Optional[float] = None


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


@app.post("/setup/data")
async def setup_data(job_info: JobInfo):
    """Find verticies, generate gcode"""

    # check if model exists
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail="No model uploaded")
    offset = (job_info.x_offset, job_info.y_offset, job_info.z_offset)
    process_stl(
        model_path, job_info.measure_length, job_info.measure_feedrate, job_info.move_feedrate, offset, job_info.z
    )

    return {"status": "ok"}


@app.get("/download/gcode")
async def download_gcode():
    """Download gcode file"""
    if not os.path.exists("data/gcode/opencmm.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    return FileResponse("data/gcode/opencmm.gcode")


@app.get("/load/image")
async def load_image():
    if not os.path.exists("data/images/result.png"):
        raise HTTPException(status_code=400, detail="No image file generated")
    return FileResponse("data/images/result.png")


@app.get("/reset/data")
async def reset_data():
    reset_tables()
    return {"status": "ok"}


@app.get("/result/points")
async def get_result_points():
    points = fetch_points()
    return {"points": points}


@app.get("/result/lines")
async def get_result_lines():
    lines = fetch_lines()
    return {"lines": lines}


@app.get("/result/arcs")
async def get_result_arcs():
    arcs = fetch_arcs()
    return {"arcs": arcs}


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
