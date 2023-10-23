from cncmark.pair import add_line_length, get_pairs
import pytest
from .config import MYSQL_CONFIG


@pytest.mark.skip(reason="not implemented")
def test_add_line_length():
    add_line_length(MYSQL_CONFIG)


@pytest.mark.skip(reason="not implemented")
def test_get_pair():
    pairs = get_pairs(MYSQL_CONFIG)
    print(pairs)
