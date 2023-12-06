from server.mark.slope import group_sides_by_pair_id, import_slopes
from server.config import MYSQL_CONFIG
from server.mark.line import get_sides
import pytest


@pytest.mark.skip(reason="Only for local testing")
def test_group_sides_by_pair_id():
    sides = get_sides(MYSQL_CONFIG, 35)
    group_sides_by_pair_id(sides)


@pytest.mark.skip(reason="Only for local testing")
def test_import_slopes():
    import_slopes(MYSQL_CONFIG, 37)
