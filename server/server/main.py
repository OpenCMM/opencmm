import uvicorn
import os
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from server.prepare import process_stl
from server.connect import connect_lines

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
    # save image
    img_path = f"data/3dmodel/{file.filename}"
    with open(img_path, "wb") as buffer:
        buffer.write(await file.read())
    process_stl(img_path, 10.0)

    return {"status": "ok"}


@app.get("/download/gcode")
async def download_gcode():
    return FileResponse("data/gcode/opencmm.gcode")


@app.get("/load/image")
async def load_image():
    connect_lines()
    return FileResponse("data/images/result.png")


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
