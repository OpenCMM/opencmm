import io
import time
from PIL import Image
import cv2
import numpy as np

from server.cmm import SingleImage
from server.coordinate import Coordinate
from picamera2 import Picamera2


class Camera:
    def __init__(self, focal_length: float, sensor_width: float) -> None:
        self.focal_length = focal_length
        self.sensor_width = sensor_width

    def start(self, is_full: bool) -> None:
        self.picam2 = Picamera2()
        if is_full:
            self.picam2.configure(self.picam2.create_still_configuration())
        else:
            self.picam2.configure(self.picam2.create_preview_configuration())
        self.picam2.start()
        time.sleep(1)

    def get_camera_wait(self):
        with open("data/gcode/camera_wait.txt", "r") as f:
            camera_wait = f.readlines()
        camera_wait = [float(x.strip()) for x in camera_wait]
        return camera_wait

def capture_images(camera: Camera, is_full: bool):
    camera.start(is_full)

    start = time.time()
    camera_wait = camera.get_camera_wait()

    for row in camera_wait:
        x, y, z, wait = row.split()
        time.sleep(wait)
        data = io.BytesIO()
        camera.picam2.capture_file(data, format='jpeg')
        print(data.getbuffer().nbytes)
        print("time :", time.time() - start)

        pil_image = Image.open(data)
        center = Coordinate(float(x), float(y), float(z))
        image_np = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        single = SingleImage(image_np, center, camera)
        single.add_real_coordinate()
