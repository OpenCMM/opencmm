from pydantic import BaseModel


class MeasurementConfig(BaseModel):
    three_d_model_id: int
    mtconnect_interval: int
    interval: int
    threshold: int


class MeasurementConfigWithProgram(BaseModel):
    program_name: str
    mtconnect_interval: int
    interval: int
    threshold: int
