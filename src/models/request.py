from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class IncidentQuery(BaseModel):
    
    query: str = Field(
        ...,
        description="The query to search for incidents",
        example="Why is checkout service latency spiking?"
    )

    service_name: str | None = Field(
        None,
        description="Specific service to investigate",
        example="checkout-service"
    )

    time_range: Literal["5m", "15m", "30m", "1h", "3h", "24h"] | None = Field(
        "15m",
        description="Time range to analyze"
    )
    
    severity: Literal["low", "medium", "high", "critical"] | None = Field(
        None,
        description="Expected severity level"
    )
    
    include_suggestions: bool = Field(
        True,
        description="Whether to include remediation suggestions"
    )

class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime
    