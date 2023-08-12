import io
import time
from PIL import Image
import cv2
import numpy as np

from picamera2 import Picamera2

def capture_images(is_full: bool):
    with open("data/gcode/camera_wait.txt", "r") as f:
        camera_wait = f.readlines()
    camera_wait = [float(x.strip()) for x in camera_wait]
    picam2 = Picamera2()
    if is_full:
        picam2.configure(picam2.create_still_configuration())

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

