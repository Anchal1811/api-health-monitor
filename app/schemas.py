from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EndpointCreate(BaseModel):
    name: str
    url: str
    interval_mins: int = 5


class EndpointResponse(BaseModel):
    id: int
    name: str
    url: str
    interval_mins: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PingLogResponse(BaseModel):
    id: int
    endpoint_id: int
    status_code: Optional[int]
    response_ms: Optional[float]
    is_up: bool
    error_msg: Optional[str]
    checked_at: datetime

    class Config:
        from_attributes = True


class EndpointStats(BaseModel):
    endpoint_id: int
    name: str
    url: str
    total_checks: int
    uptime_percent: float
    avg_response_ms: Optional[float]
    last_checked: Optional[datetime]
    current_status: str
    ssl_info: Optional[dict]