from stl import mesh
import numpy as np


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
