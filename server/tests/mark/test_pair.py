from server.mark.pair import (
    add_line_length,
    get_pairs,
    get_sides_by_pair_id,
    point_to_line_distance,
    get_edges_by_side_id,
    validate_measured_edges,
)
import pytest
from server.config import MYSQL_CONFIG

model_id = 1


@pytest.mark.skip(reason="not implemented")
def test_add_line_length():
    add_line_length(model_id, MYSQL_CONFIG)


@pytest.mark.skip(reason="not implemented")
def test_get_pair():
    pairs = get_pairs(MYSQL_CONFIG)
    print(pairs)


@pytest.mark.skip(reason="not implemented")
def test_length():
    model_id = 7
    process_id = 16
    pairs = get_pairs(model_id, MYSQL_CONFIG)
    for (pair_id,) in pairs:
        sides = get_sides_by_pair_id(pair_id, MYSQL_CONFIG)
        side1 = sides[0]
        side2 = sides[1]
        length = point_to_line_distance([side1[0:3], side1[3:6]], side2[0:3])
        print(length)
        total_measured_length = 0
        edges1 = get_edges_by_side_id(side1[6], MYSQL_CONFIG, process_id)
        edges2 = get_edges_by_side_id(side2[6], MYSQL_CONFIG, process_id)
        sample_size = 0
        line_edge_list = validate_measured_edges(edges1, edges2)
        if not line_edge_list:
            continue
        for [edges, edge] in line_edge_list:
            # check if edge is not None
            if edge and edge[0] and edge[1]:
                sample_size += 1
                total_measured_length += point_to_line_distance(edges, edge)
        if sample_size == 0:
            continue
