from cncmark.config import MYSQL_CONFIG
from stl import mesh
import numpy as np
import mysql.connector
from mysql.connector.errors import IntegrityError


def point_id(point: list):
    return f"{point[0]},{point[1]},{point[2]}"


def get_lines(stl_file_path: str, z: float):
    cuboid = mesh.Mesh.from_file(stl_file_path)
    # get vertices
    vertices = cuboid.vectors

    # Extract lines parallel to the ground
    ground_parallel_lines = []

    for facet in vertices:
        normal = np.cross(facet[1] - facet[0], facet[2] - facet[0])
        if np.isclose(normal[2], 0.0, atol=1e-6):
            # This facet is parallel to the ground
            vertices = facet.reshape(-1, 3)
            z_coords = vertices[:, 2]

            # Filter vertices based on z-coordinate
            relevant_indices = np.where(np.isclose(z_coords, z, atol=1e-6))
            relevant_vertices = vertices[relevant_indices]

            # Create lines between adjacent relevant vertices
            for i in range(len(relevant_vertices) - 1):
                line = relevant_vertices[i : i + 2]
                ground_parallel_lines.append(line)

    # remove arcs from ground_parallel_lines
    for i in range(len(ground_parallel_lines)):
        line_length = np.linalg.norm(
            ground_parallel_lines[i][0] - ground_parallel_lines[i][1]
        )
        if line_length < 1:
            ground_parallel_lines[i] = np.array([[0, 0, 0], [0, 0, 0]])

    # remove zero lines
    ground_parallel_lines = [
        line for line in ground_parallel_lines if not np.all(line == 0)
    ]
    return ground_parallel_lines


def import_lines(lines: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    line_list = [[point_id(p) for p in ab] for ab in lines]

    insert_query = "INSERT INTO line (a, b) VALUES (%s, %s)"

    try:
        cursor.executemany(insert_query, line_list)
    except IntegrityError:
        print("Error: unable to import lines")
    cnx.commit()
    cursor.close()
    cnx.close()


def get_unique_points(lines: list):
    points = []
    for line in lines:
        for point in line:
            points.append(point)
    points = np.array(points)
    unique_points = np.unique(points, axis=0)
    return unique_points


def save_unique_points(unique_points: list, file_path: str):
    with open(file_path, "w") as f:
        for point in unique_points:
            f.write(f"{point[0]},{point[1]},{point[2]}\n")


def import_points(unique_points: list):
    cnx = mysql.connector.connect(**MYSQL_CONFIG, database="coord")
    cursor = cnx.cursor()
    unique_point_list = unique_points.tolist()
    for i in range(len(unique_point_list)):
        unique_point_list[i].append(",".join(map(str, unique_point_list[i])))

    insert_query = "INSERT INTO point (x, y, z, point_id) VALUES (%s, %s, %s, %s)"

    try:
        cursor.executemany(insert_query, unique_point_list)
    except IntegrityError:
        print("Error: unable to import points")
    cnx.commit()
    cursor.close()
    cnx.close()
