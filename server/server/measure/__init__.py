from .estimate import update_data_after_measurement  # noqa: F401
from pydantic import BaseModel
import json


class EstimateConfig(BaseModel):
    process_id: int


def import_topic_payload(process_id: int):
    return json.dumps({"process_id": process_id})
