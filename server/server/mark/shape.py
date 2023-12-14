import trimesh
import numpy as np
from trimesh.graph import face_adjacency


class Shape:
    def __init__(self, stl_file_path: str):
        self.mesh = trimesh.load(stl_file_path)

    def get_unique_z_values_of_visiable_vertices(self):
        # Get the normals of the facets
        facet_normals = self.mesh.face_normals

        # Find the indices of facets facing "up" (positive z-direction)
        upward_facing_indices = np.where(facet_normals[:, 2] > 0)[0]

        # Get the unique vertices associated with upward-facing facets
        visible_vertices = np.unique(self.mesh.faces[upward_facing_indices])

        # Extract the coordinates of the visible vertices
        visible_vertex_coordinates = self.mesh.vertices[visible_vertices]

        # get unique z values
        unique_z = np.unique(visible_vertex_coordinates[:, 2])
        return unique_z

    def get_visible_facets(self):
        # Get the normals of the facets
        facet_normals = self.mesh.face_normals

        # Find the indices of facets facing "up" (positive z-direction)
        upward_facing_indices = np.where(facet_normals[:, 2] > 0)[0]

        return upward_facing_indices

    def are_coplanar(self, facet_idx0, facet_idx1, tolerance=1e-6):
        facet0 = self.mesh.vertices[self.mesh.faces[facet_idx0]]
        facet1 = self.mesh.vertices[self.mesh.faces[facet_idx1]]
        # Calculate the normal vector for each facet
        normal0 = np.cross(facet0[1] - facet0[0], facet0[2] - facet0[0])
        normal1 = np.cross(facet1[1] - facet1[0], facet1[2] - facet1[0])

        # Check if the normal vectors are parallel
        if np.all(
            np.isclose(
                normal0 / np.linalg.norm(normal0),
                normal1 / np.linalg.norm(normal1),
                atol=tolerance,
            )
        ):
            # if np.allclose(normal0, normal1):
            # Check if the facets are coplanar
            if np.all(np.abs(np.dot(facet1[0] - facet0[0], normal0)) < 1e-6):
                # The facets are coplanar
                return True
            else:
                # The facets are parallel but not coplanar
                return False
        else:
            # The facets are not coplanar
            return False

    def group_by_coplanar_facets(self, facet_indices: np.ndarray):
        """
        Group facets that are coplanar \n
        Return a list of lists of coplanar facets
        """
        coplanar_facets = [[facet_indices[0]]]
        for facet_idx in facet_indices[1:]:
            is_coplanar = False
            for i, coplanar_facet in enumerate(coplanar_facets):
                if self.are_coplanar(facet_idx, coplanar_facet[0]):
                    coplanar_facets[i].append(facet_idx)
                    is_coplanar = True
                    break
            if not is_coplanar:
                coplanar_facets.append([facet_idx])
                is_coplanar = False

        return coplanar_facets

    def get_lines_and_arcs(self, arc_threshold: int = 1):
        shapes = self.get_shapes()
        lines = []
        arcs = []

        previous_length = 0
        for coplanar_shapes in shapes:
            line_group = []
            arc_group = []
            for i in range(len(coplanar_shapes)):
                point0 = self.mesh.vertices[coplanar_shapes[i][0]]
                point1 = self.mesh.vertices[coplanar_shapes[i][1]]
                point = np.array([point0, point1])
                line_length = np.linalg.norm(point0 - point1)
                if line_length > arc_threshold:
                    # line
                    line_group.append(point)
                else:
                    # arc
                    # if close to previous length, add to previous arc
                    if np.isclose(line_length, previous_length, atol=1e-3):
                        arc_group[-1] = np.vstack((arc_group[-1], point1))
                    else:
                        arc_group.append(point)

                previous_length = line_length

            if line_group:
                lines.append(line_group)
            if arc_group:
                arcs.append(arc_group)

        return lines, arcs

    def get_shapes(self):
        """
        Extract lines and arcs from an STL file \n
        If the line length is less than 1, it is considered an arc. \n
        if the line length for an arc is close to the previous arc length,
        it is considered part of the previous arc. \n
        Note: This is not a robust algorithm.
        """
        visible_facet_indices = self.get_visible_facets()
        group_facets = self.group_by_coplanar_facets(visible_facet_indices)
        adjacency = face_adjacency(self.mesh.faces)

        shapes = []
        for coplanar_facets in group_facets:
            shapes_on_coplanar_facet = []
            for pair in adjacency:
                pair0_in_group = pair[0] in coplanar_facets
                pair1_in_group = pair[1] in coplanar_facets
                if pair0_in_group != pair1_in_group:
                    common_edge_vertices = list(
                        set(self.mesh.faces[pair[0]]) & set(self.mesh.faces[pair[1]])
                    )
                    if pair0_in_group:
                        face_id = pair[1]
                    else:
                        face_id = pair[0]
                    common_edge_vertices.append(face_id)
                    shapes_on_coplanar_facet.append(common_edge_vertices)

            # order by face index
            shapes_on_coplanar_facet.sort(key=lambda x: x[-1])
            shapes.append(shapes_on_coplanar_facet)

        return shapes
