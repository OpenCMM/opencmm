from stl import mesh
import numpy as np
import trimesh


def point_id(point: np.ndarray):
    return ",".join(point.astype(str))


def get_highest_z(vertices):
    # get highest point
    highest_point = np.max(vertices, axis=0)
    return highest_point[2][2]


def get_shapes(stl_file_path: str, decimal_places: int = 3):
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

    Returns
    -------
    ground_parallel_lines : np.ndarray
        numpy array of lines parallel to the ground
    ground_parallel_arcs : list
        List of arcs parallel to the ground
    """
    cuboid = mesh.Mesh.from_file(stl_file_path)
    # get vertices
    vertices = cuboid.vectors
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
            if np.isclose(line_length, previous_length, atol=1e-3):
                ground_parallel_arcs[-1] = np.vstack(
                    (ground_parallel_arcs[-1], ground_parallel_shapes[i][1])
                )
            else:
                ground_parallel_arcs.append(ground_parallel_shapes[i])

        previous_length = line_length

    # round to decimal places
    ground_parallel_lines = round_shape_values(ground_parallel_lines, decimal_places)
    ground_parallel_arcs = round_shape_values(ground_parallel_arcs, decimal_places)

    return np.array(ground_parallel_lines), ground_parallel_arcs


def round_shape_values(shapes: np.ndarray, decimal_places: int = 3):
    for i in range(len(shapes)):
        shapes[i] = np.round(shapes[i], decimals=decimal_places)

    return shapes


def ray_cast(stl_file_path: str, ray_origin: tuple):
    """
    Check if a point hits an STL file

    Parameters
    ----------
    stl_file_path : str
        Path to STL file
    ray_origin : tuple
        Point to check

    Returns
    -------
    hit : bool
        True if point hits STL file
    """
    mesh = trimesh.load_mesh(stl_file_path)
    ray_origins = np.array([ray_origin])
    ray_directions = np.array([[0, 0, -1]])

    # Check if the ray intersects the mesh
    index = mesh.ray.intersects_first(ray_origins, ray_directions)[0]
    return index != -1


def get_visible_lines(stl_file_path: str, decimal_places: int = 3):
    mesh = trimesh.load(stl_file_path)

    # Get the normals of the facets
    facet_normals = mesh.face_normals

    # Find the indices of facets facing "up" (positive z-direction)
    upward_facing_indices = np.where(facet_normals[:, 2] > 0)[0]

    lines = []
    for idx in upward_facing_indices:
        vertices = mesh.vertices[mesh.faces[idx]]
        # add each line in the triangle
        lines.append([vertices[0].tolist(), vertices[1].tolist()])
        lines.append([vertices[1].tolist(), vertices[2].tolist()])
        lines.append([vertices[2].tolist(), vertices[0].tolist()])

    # sort lines by x, y
    for line in lines:
        if line[0][0] > line[1][0]:
            line[0], line[1] = line[1], line[0]
        elif line[0][0] == line[1][0]:
            if line[0][1] > line[1][1]:
                line[0], line[1] = line[1], line[0]

    lines = np.array(lines)
    unique_lines = np.unique(lines, axis=0)
    return round_shape_values(unique_lines, decimal_places)
