from server.mark.pair import (
    add_line_length,
    get_pairs,
)
import pytest
from server.config import MYSQL_CONFIG

model_id = 1


@pytest.mark.skip(reason="Only for local testing")
def test_add_line_length():
    add_line_length(model_id, MYSQL_CONFIG, 3)


@pytest.mark.skip(reason="not implemented")
def test_get_pair():
    pairs = get_pairs(MYSQL_CONFIG)
    print(pairs)
