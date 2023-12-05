import numpy as np
import trimesh
from itertools import combinations


class Shape:
    def __init__(self, stl_file_path: str):
        self.mesh = trimesh.load(stl_file_path)
    
    def get_visible_facets(self):
        # Get the normals of the facets
        facet_normals = self.mesh.face_normals

        # Find the indices of facets facing "up" (positive z-direction)
        upward_facing_indices = np.where(facet_normals[:, 2] > 0)[0]

        return self.mesh.faces[upward_facing_indices]

    def group_by_coplanar_facets(self, facets):
        coplanar_facets = [[facets[0]]]
        for facet in facets[1:]:
            for i, coplanar_facet in enumerate(coplanar_facets):
                if are_facets_on_same_plane(facet, coplanar_facet[0]):
                    coplanar_facets[i].append(facet)
                    break
                else:
                    coplanar_facets.append([facet])

        return coplanar_facets


    def get_unique_z_values_of_visiable_vertices(self):
        visible_facets = self.get_visible_facets()
        # Get the unique vertices associated with upward-facing facets
        visible_vertices = np.unique(visible_facets)

        # Extract the coordinates of the visible vertices
        visible_vertex_coordinates = self.mesh.vertices[visible_vertices]

        # get unique z values
        unique_z = np.unique(visible_vertex_coordinates[:, 2])
        return unique_z

    def get_shapes(self, decimal_places: int = 3):
        """
        Extract lines and arcs from an STL file \n
        If the line length is less than 1, it is considered an arc. \n
        if the line length for an arc is close to the previous arc length,
        it is considered part of the previous arc. \n
        Note: This is not a robust algorithm.
        """
        # get vertices
        vertices = self.mesh.faces
        unique_z_values = self.get_unique_z_values_of_visiable_vertices()

        # Extract lines and arcs parallel to the ground
        shapes = []
        lines = []
        arcs = []

        for _facet in vertices:
            facet = self.mesh.vertices[_facet]
            normal = np.cross(facet[1] - facet[0], facet[2] - facet[0])
            if np.isclose(normal[2], 0.0, atol=1e-6):
                # This facet is parallel to the ground
                vertices = facet.reshape(-1, 3)
                z_coords = vertices[:, 2]

                # Filter vertices based on z-coordinate
                for z in unique_z_values:
                    relevant_indices = np.where(np.isclose(z_coords, z, atol=1e-6))
                    relevant_vertices = vertices[relevant_indices]

                    # Create shapes between adjacent relevant vertices
                    for i in range(len(relevant_vertices) - 1):
                        line = relevant_vertices[i : i + 2]
                        shapes.append(line)

        previous_length = 0
        for i in range(len(shapes)):
            line_length = np.linalg.norm(
                shapes[i][0] - shapes[i][1]
            )
            if line_length > 1:
                # line
                lines.append(shapes[i])
            else:
                # arc
                # if close to previous length, add to previous arc
                if np.isclose(line_length, previous_length, atol=1e-3):
                    arcs[-1] = np.vstack(
                        (arcs[-1], shapes[i][1])
                    )
                else:
                    arcs.append(shapes[i])

            previous_length = line_length

        # round to decimal places
        lines = round_shape_values(
            lines, decimal_places
        )
        arcs = round_shape_values(arcs, decimal_places)

        return np.array(lines), arcs


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
    return mesh.ray.intersects_any(ray_origins, ray_directions)[0]


def get_visible_facets(stl_file_path: str):
    # Load the STL file
    mesh = trimesh.load(stl_file_path)

    # Get the normals of the facets
    facet_normals = mesh.face_normals

    # Find the indices of facets facing "up" (positive z-direction)
    upward_facing_indices = np.where(facet_normals[:, 2] > 0)[0]

    return mesh.vertices[mesh.faces[upward_facing_indices]]


def are_adjacent_facets(facet1, facet2):
    # Extract vertices from each facet
    facet1_vertices = facet1.reshape(-1, 3)
    facet2_vertices = facet2.reshape(-1, 3)

    # Initialize counter
    shared_vertices = 0

    # Compare vertices
    for vertex1 in facet1_vertices:
        for vertex2 in facet2_vertices:
            if np.array_equal(vertex1, vertex2):
                shared_vertices += 1

    # Check adjacency
    if shared_vertices == 2:
        return True
    else:
        return False


def are_facets_on_same_plane(facet1, facet2, tolerance=1e-6):
    normal1 = np.cross(facet1[1] - facet1[0], facet1[2] - facet1[0])
    normal2 = np.cross(facet2[1] - facet2[0], facet2[2] - facet2[0])

    # Check if the cross products (normal vectors) are parallel
    return np.all(
        np.isclose(
            normal1 / np.linalg.norm(normal1),
            normal2 / np.linalg.norm(normal2),
            atol=tolerance,
        )
    )


def group_by_coplanar_facets(facets):
    coplanar_facets = [[facets[0]]]
    for facet in facets[1:]:
        for i, coplanar_facet in enumerate(coplanar_facets):
            if are_facets_on_same_plane(facet, coplanar_facet[0]):
                coplanar_facets[i].append(facet)
                break
            else:
                coplanar_facets.append([facet])

    return coplanar_facets


def get_facet_corner(facet, duplicate_points):
    all = np.concatenate((facet, duplicate_points), axis=0)
    _unique, counts = np.unique(all, axis=0, return_counts=True)
    return _unique[np.where(counts == 1)][0]


def get_lines_on_coplanar_facets(facets):
    adjacent_facets = []
    for i, j in combinations(range(len(facets)), 2):
        # if two facets share two vertices, they are adjacent
        if are_adjacent_facets(facets[i], facets[j]):
            adjacent_facets.append([facets[i], facets[j]])

    lines = []
    # check if adjacent facets are coplanar, if yes, merge them
    for i in range(len(adjacent_facets)):
        # get two adjacent facets
        facet1 = adjacent_facets[i][0]
        facet2 = adjacent_facets[i][1]
        if are_facets_on_same_plane(facet1, facet2):
            unique_points, counts = np.unique(
                np.concatenate((facet1, facet2), axis=0), axis=0, return_counts=True
            )
            # duplicate points are the points that are shared by two facets
            duplicate_points = unique_points[counts > 1]
            facet1_corner = get_facet_corner(facet1, duplicate_points)
            facet2_corner = get_facet_corner(facet2, duplicate_points)

            facet_lines = []
            facet_lines.append(
                np.array(
                    [
                        np.array([facet1_corner, duplicate_points[0]]),
                        np.array([facet2_corner, duplicate_points[1]]),
                    ]
                )
            )
            facet_lines.append(
                np.array(
                    [
                        [facet1_corner, duplicate_points[1]],
                        [facet2_corner, duplicate_points[0]],
                    ]
                )
            )
            lines.append(facet_lines)

    return lines


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
