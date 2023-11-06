from server.mark.point import (
    get_highest_z,
)
from stl import mesh


def test_get_highest_point():
    cuboid = mesh.Mesh.from_file("tests/fixtures/stl/sample.stl")
    # get vertices
    vertices = cuboid.vectors
    highest_z = get_highest_z(vertices)
    assert highest_z == 10.0
