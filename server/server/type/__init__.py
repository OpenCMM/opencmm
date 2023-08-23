from typing import Optional
from pydantic import BaseModel

class JobInfo(BaseModel):
    camera_height: float
    feed_rate: float
    x_offset: Optional[float]
    y_offset: Optional[float]
    z_offset: Optional[float]
    z: Optional[float] = None


class CameraInfo(BaseModel):
    focal_length: float
    sensor_width: float
    distance: float
    is_full: bool = False
    save_as_file: bool = False
