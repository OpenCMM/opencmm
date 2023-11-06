from server.prepare import program_number_to_model_id


def test_program_number_to_model_id():
    program_name = "1001"
    model_id = program_number_to_model_id(program_name)
    assert model_id == 1

    program_name = "2332 MIZO"
    model_id = program_number_to_model_id(program_name)
    assert model_id is None
