from cncmark.config import MYSQL_CONFIG
from stl import mesh
import numpy as np
import mysql.connector
from mysql.connector.errors import IntegrityError
from typing import Optional


def point_id(point: list):
    return f"{point[0]},{point[1]},{point[2]}"


def get_highest_z(vertices):
    # get highest point
    highest_point = np.max(vertices, axis=0)
    return highest_point[2][2]


def get_shapes(stl_file_path: str, z: Optional[float]):
    """
    Extract lines parallel to the ground from an STL file \n
    If the line length is less than 1, it is considered an arc. \n
    if the line length for an arc is close to the previous arc length,
    it is considered part of the previous arc. \n
    Note: This is not a robust algorithm.

    Parameters
    ----------
    stl_file_path : str
        Path to STL file
    z : float
        z-coordinate of the plane parallel to the ground

    Returns
    -------
    ground_parallel_lines : list
        List of lines parallel to the ground
    ground_parallel_arcs : list
        List of arcs parallel to the ground
    """
    cuboid = mesh.Mesh.from_file(stl_file_path)
    # get vertices
    vertices = cuboid.vectors
    if z is None:
        z = get_highest_z(vertices)

    # Extract lines and arcs parallel to the ground
    ground_parallel_shapes = []
    ground_parallel_lines = []
    ground_parallel_arcs = []

    for facet in vertices:
        normal = np.cross(facet[1] - facet[0], facet[2] - facet[0])
        if np.isclose(normal[2], 0.0, atol=1e-6):
            # This facet is parallel to the ground
            vertices = facet.reshape(-1, 3)
            z_coords = vertices[:, 2]

            # Filter vertices based on z-coordinate
            relevant_indices = np.where(np.isclose(z_coords, z, atol=1e-6))
            relevant_vertices = vertices[relevant_indices]

            # Create shapes between adjacent relevant vertices
            for i in range(len(relevant_vertices) - 1):
                line = relevant_vertices[i : i + 2]
                ground_parallel_shapes.append(line)

    previous_length = 0
    for i in range(len(ground_parallel_shapes)):
        line_length = np.linalg.norm(
            ground_parallel_shapes[i][0] - ground_parallel_shapes[i][1]
        )
        if line_length > 1:
            # line
            ground_parallel_lines.append(ground_parallel_shapes[i])
        else:
            # arc
            # if close to previous length, add to previous arc
            if np.isclose(line_length, previous_length, atol=1e-6):
                ground_parallel_arcs[-1] = np.vstack(
                    (ground_parallel_arcs[-1], ground_parallel_shapes[i][1])
                )
            else:
                ground_parallel_arcs.append(ground_parallel_shapes[i])

        previous_length = line_length

    return ground_parallel_lines, ground_parallel_arcs


def get_unique_points(lines: list, arcs: list):
    from .arc import pick_arc_points

    points = []
    for line in lines:
        for point in line:
            points.append(point)

    for arc in arcs:
        arc_points = pick_arc_points(arc)
        for point in arc_points:
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
