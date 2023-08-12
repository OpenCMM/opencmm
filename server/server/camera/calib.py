import cv2
import json
import numpy as np


def undistort_img(img, camera_data_path: str):
    h, w = img.shape[:2]
    camera_matrix, dist_coefs = get_camera_data(camera_data_path)
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coefs, (w, h), 1, (w, h)
    )

    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    # crop and save the image
    x, y, w, h = roi
    dst = dst[y : y + h, x : x + w]
    return dst


def get_camera_data(camera_data_path: str):
    with open(camera_data_path, "r") as f:
        data = json.load(f)
        camera_matrix = np.array(data["camera_matrix"])
        dist_coefs = np.array(data["distortion_coefficients"])

    return camera_matrix, dist_coefs
