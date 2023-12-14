from pydantic import BaseModel
from typing import Optional


class GcodeSettings(BaseModel):
    three_d_model_id: int
    measurement_range: float
    measure_feedrate: float
    move_feedrate: float
    x_offset: Optional[float] = 0.0
    y_offset: Optional[float] = 0.0
    z_offset: Optional[float] = 0.0
    send_gcode: Optional[bool] = True
