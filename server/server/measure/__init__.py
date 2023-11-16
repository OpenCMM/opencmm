from .estimate import update_data_after_measurement  # noqa: F401
from pydantic import BaseModel


class EstimateConfig(BaseModel):
    process_id: int
