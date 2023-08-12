import io
import time
from PIL import Image
import cv2
import numpy as np
from server.camera import Camera
from server.cmm import SingleImage
from server.coordinate import Coordinate
from picamera2 import Picamera2

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


def buffer_to_image(is_full: bool):
    picam2 = Picamera2()
    if is_full:
        picam2.configure(picam2.create_still_configuration())
    else:
        picam2.configure(picam2.create_preview_configuration())
    picam2.start()

    time.sleep(1)
    start = time.time()
    data = io.BytesIO()
    picam2.capture_file(data, format='jpeg')
    print(data.getbuffer().nbytes)
    print("time :", time.time() - start)

    pil_image = Image.open(data)
    image_np = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return image_np

