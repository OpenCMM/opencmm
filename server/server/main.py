import uvicorn
import os
from fastapi import FastAPI, UploadFile, HTTPException, WebSocket
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from server.prepare import process_stl
from server.camera import Camera
from server.capture import capture_images
from server.reset import reset_tables
from server.result import fetch_points, fetch_arcs, fetch_lines
import board
import busio
import adafruit_vl53l0x
import time
import asyncio
from server.type import JobInfo, CameraInfo

model_path = "data/3dmodel/3dmodel.stl"

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)
vl53.measurement_timing_budget = 200000

connected_websockets = set()

async def measure_distance():
    with vl53.continuous_mode():
        while True:
            distance = vl53.range
            timestamp = time.time()
            data = {"distance": distance, "timestamp": timestamp}
            
            for websocket in connected_websockets:
                await websocket.send_json(data)
            
            await asyncio.sleep(0.1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(e)
        connected_websockets.remove(websocket)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(measure_distance())


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
        model_path, job_info.camera_height, job_info.feed_rate, offset, job_info.z
    )

    return {"status": "ok"}


@app.post("/process/start")
async def process_start(camera_info: CameraInfo):
    camera = Camera(camera_info.focal_length, camera_info.sensor_width)
    capture_images(
        camera, camera_info.distance, camera_info.is_full, camera_info.save_as_file
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
