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
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="Diagnosis status (success, partial, failed)")
    query: str = Field(..., description="Original user query")
    
    # Analysis result (free-form text from LLM)
    analysis: str = Field(..., description="AI-generated analysis and recommendations")
    
    # Metadata
    tools_executed: List[ToolExecution] = Field(
        default_factory=list,
        description="List of tools executed during diagnosis"
    )
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    timestamp: str = Field(..., description="ISO format timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_a1b2c3d4",
                "status": "success",
                "query": "Why is checkout service slow?",
                "analysis": "Based on the logs and metrics analysis:\n\nRoot Cause: Database connection pool exhausted (100/100 connections active)\n\nEvidence:\n- 25 ERROR logs showing 'connection pool exhausted'\n- CPU usage spiked to 95%\n- Response time increased from 250ms to 3500ms\n- Error rate jumped from 0.5% to 15%\n\nRecommendations:\n1. Increase database connection pool size from 100 to 200\n2. Add connection timeout monitoring and alerts\n3. Investigate sudden traffic increase (300% spike detected)",
                "tools_executed": [
                    {
                        "tool_name": "query_logs",
                        "execution_time_ms": 125,
                        "result_summary": "Found 25 logs",
                        "data_points": 25
                    },
                    {
                        "tool_name": "query_metrics",
                        "execution_time_ms": 89,
                        "result_summary": "Retrieved 4 metric types",
                        "data_points": 15
                    }
                ],
                "processing_time_ms": 3245,
                "timestamp": "2024-12-06T10:50:30.123456Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str | None = None
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)