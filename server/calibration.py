"""
Calibration functions for the camera
"""
import cv2
import os
import numpy as np

image_path = "calibration_images"

# Checkerboard parameters
num_cols = 10
num_rows = 7
square_size_mm = 11.25

# Prepare object points in real-world coordinates (assuming the Z-axis is 0 since the checkerboard is on a plane)
objp = np.zeros((num_cols * num_rows, 3), np.float32)
objp[:, :2] = np.mgrid[0:num_cols, 0:num_rows].T.reshape(-1, 2) * square_size_mm

# Arrays to store object points and image points from all the images.
obj_points = []  # 3D points in real world space
img_points = []  # 2D points in image plane.

def list_files(folder_name):
	"""
	List all files in a folder
	"""
	return [f for f in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, f))]


def get_camera_calibration(image_path, num_cols, num_rows):
    calibration_image_files = list_files(image_path)

    # # downscale the images to speed up the processing
    # for img_file in calibration_images_files:
    #     img_path = f"checker_board_images/{img_file}"
    #     cv2.imwrite(img_path, cv2.resize(cv2.imread(img_path), (0, 0), fx=0.5, fy=0.5))

    for img_file in calibration_image_files:
        img_path = f"{image_path}/{img_file}"
        img = cv2.imread(img_path)
        assert img is not None, f"Failed to load image at {img_path}"
        print(f"Processing {img_path}...")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (num_cols, num_rows), None)

        # If found, add object points and image points
        if ret:
            obj_points.append(objp)
            img_points.append(corners)

            # Draw and display the corners (optional, just for visual inspection)
            cv2.drawChessboardCorners(img, (num_cols, num_rows), corners, ret)
            cv2.imshow('img', img)
            cv2.waitKey(500)  # Wait for 0.5 seconds

    cv2.destroyAllWindows()

    # Calibrate the camera
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

    # Print the camera matrix and distortion coefficients
    print("Camera Matrix:")
    print(camera_matrix)
    print("\nDistortion Coefficients:")
    print(dist_coeffs)

    # save as file
    np.savez("camera_calibration.npz", camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)

# get_camera_calibration(image_path, num_cols, num_rows)

# load file
npzfile = np.load("camera_calibration.npz")

camera_matrix = npzfile["camera_matrix"]
dist_coeffs = npzfile["dist_coeffs"]

# undistort image
# load image
img_path = f"{image_path}/easy2.jpg"
img = cv2.imread(img_path)
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
    camera_matrix, dist_coeffs, (w,h), 1, (w,h))

# undistort
dst = cv2.undistort(img, camera_matrix, dist_coeffs, None, newcameramtx)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png', dst)

focal_length = camera_matrix[0,0]
print(focal_length)