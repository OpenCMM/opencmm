from pydantic import BaseModel


class MTConnectConfig(BaseModel):
    url: str
    interval: int
    latency: int
