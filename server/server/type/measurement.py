from pydantic import BaseModel


class MeasurementConfig(BaseModel):
    three_d_model_id: int


class MeasurementConfigWithProgram(BaseModel):
    program_name: str
