from pydantic import BaseModel


class SensorConfig(BaseModel):
    interval: int
    threshold: int
    beam_diameter: float
    middle_output: float
    response_time: float
    tolerance: float
