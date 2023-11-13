from server.mark.edge import get_edge_ids_order_by_x_y
from server.config import MYSQL_CONFIG

model_id = 1


def test_get_edge_ids_order_by_x_y():
    get_edge_ids_order_by_x_y(model_id, MYSQL_CONFIG)
