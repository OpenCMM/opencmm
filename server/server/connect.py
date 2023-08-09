from cnceye.cmm import AllImages
from cnceye.camera import Camera

focal_length = 50.0  # mm
camera_height = 60.0  # mm
object_height = 10.0  # mm
distance = camera_height - object_height
sensor_width = 36.0  # mm
camera = Camera(focal_length, sensor_width)

def connect_lines():
    all_images = AllImages(camera)
    all_images.add_lines()
    all_images.save_image("data/images/result.png")