from server.model import get_model_data


def test_get_model_data():
    _model_id = 100
    model_id = get_model_data(_model_id)
    assert model_id is None
