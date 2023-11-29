from server.mark.step import import_steps
from server.config import MYSQL_CONFIG
import pytest


@pytest.mark.skip(reason="Only for local testing")
def test_import_steps():
    import_steps(MYSQL_CONFIG, 22)
    assert 1 == 1
