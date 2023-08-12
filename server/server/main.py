import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from server.prepare import process_stl
from server.connect import connect_lines
from pydantic import BaseModel
import os
from server.camera import Camera
from server.capture import capture_images


class JobInfo(BaseModel):
    z: float
    camera_height: float
    feed_rate: float


class CameraInfo(BaseModel):
    focal_length: float
    sensor_width: float
    distance: float
    is_full: bool = False


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
    process_stl(model_path, job_info.z, job_info.camera_height, job_info.feed_rate)

    return {"status": "ok"}


@app.post("/process/start")
async def process_start(camera_info: CameraInfo):
    camera = Camera(camera_info.focal_length, camera_info.sensor_width)
    capture_images(camera, camera_info.distance, camera_info.is_full)

    return {"status": "ok"}


@app.get("/download/gcode")
async def download_gcode():
    """Download gcode file"""
    if not os.path.exists("data/gcode/opencmm.gcode"):
        raise HTTPException(status_code=400, detail="No gcode file generated")
    return FileResponse("data/gcode/opencmm.gcode")


@app.get("/load/image")
async def load_image():
    connect_lines()
    if not os.path.exists("data/images/result.png"):
        raise HTTPException(status_code=400, detail="No image file generated")
    return FileResponse("data/images/result.png")


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
