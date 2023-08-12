import time

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
        camera_wait = [format_row(x.strip()) for x in camera_wait]
        return camera_wait
    
    def stop(self):
        self.picam2.stop()

def format_row(row: str) -> list:
    return [float(x) for x in row.split()]
