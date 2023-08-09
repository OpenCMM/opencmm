from camera.capture import add_img_path
import pytest


@pytest.mark.skip(reason="need to mock mysql")
def test_add_img_path():
    index = 0
    with open("tests/fixtures/coordinates.txt", "r") as f:
        for line in f:
            point_id = line.strip()
            img_path = f"/home/piyuchi/Pictures/image_{index}.jpg"
            add_img_path(img_path, point_id)
            index += 1
