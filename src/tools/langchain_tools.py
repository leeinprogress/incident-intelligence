"""
LangChain Tool Wrappers

This module wraps existing MCP tools (LogsQueryTool, MetricsQueryTool) 
as LangChain StructuredTools for use with LangChain agents.

Key Features:
- Pydantic schema definitions for type safety
- Async support for tool execution
- Reuses existing tool logic (no duplication)
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from src.mcp_tools import LogsQueryTool, MetricsQueryTool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ========================
# Pydantic Input Schemas
# ========================

class LogsQueryInput(BaseModel):
    """Input schema for query_logs tool"""
    service_name: str = Field(
        default="all",
        description="Name of the service to query (e.g., 'checkout-service', 'payment-service') or 'all' for all services"
    )
    time_range: str = Field(
        default="15m",
        description="Time range to query: 5m, 15m, 30m, 1h, 3h, or 24h"
    )
    severity: str = Field(
        default="all",
        description="Log severity level to filter: info, warning, error, critical, or all"
    )
    limit: int = Field(
        default=100,
        description="Maximum number of logs to return (1-1000)",
        ge=1,
        le=1000
    )


class MetricsQueryInput(BaseModel):
    """Input schema for query_metrics tool"""
    service_name: str = Field(
        default="all",
        description="Name of the service to query or 'all' for all services"
    )
    metric_type: str = Field(
        default="all",
        description="Type of metric to query: cpu, memory, latency, error_rate, or all"
    )
    time_range: str = Field(
        default="15m",
        description="Time range to query: 5m, 15m, 30m, 1h, 3h, or 24h"
    )


# ========================
# Tool Instances
# ========================

# Initialize existing tools once (singleton pattern)
_logs_tool = LogsQueryTool()
_metrics_tool = MetricsQueryTool()


# ========================
# Tool Functions
# ========================

async def query_logs_func(
    service_name: str = "all",
    time_range: str = "15m",
    severity: str = "all",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Query application logs to investigate errors, warnings, and events.
    
    This function wraps the existing LogsQueryTool and is compatible with LangChain agents.
    
    Args:
        service_name: Service to query logs from
        time_range: Time window for log retrieval
        severity: Minimum severity level to include
        limit: Maximum number of log entries
        
    Returns:
        Dictionary containing logs data with success status and execution time
    """
    logger.info(
        "LangChain tool called: query_logs",
        extra={
            "service_name": service_name,
            "time_range": time_range,
            "severity": severity,
            "limit": limit
        }
    )
    
    # Call existing tool's run method
    result = await _logs_tool.run(
        service_name=service_name,
        time_range=time_range,
        severity=severity,
        limit=limit
    )
    
    return result


async def query_metrics_func(
    service_name: str = "all",
    metric_type: str = "all",
    time_range: str = "15m"
) -> Dict[str, Any]:
    """
    Query system metrics like CPU usage, memory, latency, and error rates.
    
    This function wraps the existing MetricsQueryTool and is compatible with LangChain agents.
    
    Args:
        service_name: Service to query metrics from
        metric_type: Type of metrics to retrieve
        time_range: Time window for metric data
        
    Returns:
        Dictionary containing metrics data with success status and execution time
    """
    logger.info(
        "LangChain tool called: query_metrics",
        extra={
            "service_name": service_name,
            "metric_type": metric_type,
            "time_range": time_range
        }
    )
    
    # Call existing tool's run method
    result = await _metrics_tool.run(
        service_name=service_name,
        metric_type=metric_type,
        time_range=time_range
    )
    
    return result


# ========================
# LangChain StructuredTools
# ========================

query_logs_tool = StructuredTool.from_function(
    func=query_logs_func,
    name="query_logs",
    description=(
        "Query application logs to investigate errors, warnings, and events in the system. "
        "Use this tool when you need to understand what errors occurred, when they happened, "
        "and which services were affected. Returns structured log entries with timestamps, "
        "severity levels, and messages."
    ),
    args_schema=LogsQueryInput,
    return_direct=False,
    coroutine=query_logs_func  # Async support
)

query_metrics_tool = StructuredTool.from_function(
    func=query_metrics_func,
    name="query_metrics",
    description=(
        "Query system metrics like CPU usage, memory utilization, latency, and error rates. "
        "Use this tool to understand system performance, identify resource bottlenecks, "
        "and correlate performance issues with incidents. Returns time-series metric data "
        "with current values and trends."
    ),
    args_schema=MetricsQueryInput,
    return_direct=False,
    coroutine=query_metrics_func  # Async support
)


# ========================
# Tools List (for easy import)
# ========================

tools = [query_logs_tool, query_metrics_tool]


# Export for convenience
__all__ = [
    "query_logs_tool",
    "query_metrics_tool",
    "tools",
    "LogsQueryInput",
    "MetricsQueryInput"
]

