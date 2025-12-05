from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class DiagnosisStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ToolExecution(BaseModel):
    """Information about a tool execution"""
    tool_name: str
    execution_time_ms: int
    result_summary: str
    data_points: int


class DiagnosisResponse(BaseModel):
    """Response model for incident diagnosis"""
    
    request_id: str = Field(..., description="Unique request identifier")
    status: DiagnosisStatus
    query: str
    
    # Analysis results
    root_cause: str | None = Field(None, description="Identified root cause")
    affected_services: List[str] = Field(default_factory=list)
    timeline: str | None = Field(None, description="Incident timeline")
    
    # Supporting data
    logs_analyzed: int = 0
    metrics_analyzed: int = 0
    tools_executed: List[ToolExecution] = Field(default_factory=list)
    
    # Recommendations
    suggestions: List[str] = Field(default_factory=list)
    related_issues: List[str] = Field(default_factory=list)
    
    # Metadata
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    processing_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123456",
                "status": "success",
                "query": "Why is checkout service slow?",
                "root_cause": "Database connection pool exhausted",
                "affected_services": ["checkout-service", "payment-service"],
                "logs_analyzed": 1523,
                "metrics_analyzed": 45,
                "suggestions": [
                    "Increase DB connection pool size",
                    "Add connection timeout monitoring"
                ],
                "confidence_score": 0.85,
                "processing_time_ms": 3200
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str | None = None
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)