from pydantic import BaseModel


class SensorConfig(BaseModel):
    interval: int
    threshold: int
