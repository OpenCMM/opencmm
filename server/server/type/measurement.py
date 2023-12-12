from pydantic import BaseModel


class MeasurementConfig(BaseModel):
    three_d_model_id: int


class MeasurementConfigWithProgram(BaseModel):
    program_name: str


class EdgeDetectionConfig(BaseModel):
    arc_number: int
    line_number: int


class TraceConfig(BaseModel):
    min_measure_count: int
    max_feedrate: int
    interval: int
    margin: float
    slope_number: int
