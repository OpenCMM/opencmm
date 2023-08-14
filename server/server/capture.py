import io
import time
from PIL import Image
import cv2
import numpy as np
from server.camera import Camera
from server.cmm import SingleImage, AllImages
from server.coordinate import Coordinate
from picamera2 import Picamera2


def capture_images(camera: Camera, distance: float, is_full: bool, save_as_file: bool):
    start = time.time()
    process_time = 0
    camera.start(is_full)

    camera_wait = camera.get_camera_wait()

    for i, row in enumerate(camera_wait):
        x, y, z, wait = row

        if i == 0:
            elapsed = time.time() - start
            print("elapsed :", elapsed, "wait :", wait)
            if elapsed < wait:
                time.sleep(wait - elapsed)
        else:
            print("process_time :", process_time, "wait :", wait)
            if process_time < wait:
                time.sleep(wait - process_time)

        capture_start = time.time()
        if save_as_file:
            camera.picam2.capture_file(f"data/images/{i}.jpg", format="jpeg")
            print("capture time :", time.time() - capture_start)
            center = Coordinate(float(x), float(y), float(z))
            image = cv2.imread(f"data/images/{i}.jpg")
            single = SingleImage(image, center, camera)
            single.add_real_coordinate(distance)
        else:
            data = io.BytesIO()
            camera.picam2.capture_file(f"data/images/{i}.jpg", format="jpeg")

            camera.picam2.capture_file(data, format="jpeg")
            print(data.getbuffer().nbytes)
            print("capture time :", time.time() - capture_start)

            pil_image = Image.open(data)
            center = Coordinate(float(x), float(y), float(z))
            image_np = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            single = SingleImage(image_np, center, camera)
            single.add_real_coordinate(distance)

        process_time = time.time() - capture_start

    camera.stop()

    all_images = AllImages(camera)
    all_images.add_lines()
    all_images.add_arcs()
    all_images.save_image("data/images/result.png")


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
    picam2.capture_file(data, format="jpeg")
    print(data.getbuffer().nbytes)
    print("time :", time.time() - start)

    pil_image = Image.open(data)
    image_np = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return image_np
