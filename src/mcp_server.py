"""
MCP Server for Incident Intelligence

This server exposes diagnostic tools (logs and metrics querying) 
through the Model Context Protocol using FastMCP.
"""

from fastmcp import FastMCP
from typing import Dict, Any
import asyncio

from src.mcp_tools.logs_tool import LogsQueryTool
from src.mcp_tools.metrics_tool import MetricsQueryTool
from src.utils.logger import setup_logging, get_logger
from src.config import settings


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("incident-intelligence")

# Initialize tool instances
logs_tool = LogsQueryTool()
metrics_tool = MetricsQueryTool()


@mcp.tool()
async def query_logs(
    service_name: str = "all",
    time_range: str = "15m",
    severity: str = "all",
    limit: int = 100
) -> Dict[str, Any]:
    """
    Query application logs to find errors, warnings, and events.
    
    Use this to investigate what happened in the system.
    
    Args:
        service_name: Name of the service to query (e.g., 'checkout-service', 'payment-service') or 'all' for all services
        time_range: Time range to query (5m, 15m, 30m, 1h, 3h, 24h)
        severity: Log severity level to filter (info, warning, error, critical, all)
        limit: Maximum number of logs to return
    
    Returns:
        Dictionary containing log entries with timestamps, severity levels, and messages
    """
    logger.info(
        "MCP tool called: query_logs",
        extra={
            "service_name": service_name,
            "time_range": time_range,
            "severity": severity,
            "limit": limit
        }
    )
    
    result = await logs_tool.run(
        service_name=service_name,
        time_range=time_range,
        severity=severity,
        limit=limit
    )
    
    logger.info(
        "query_logs completed",
        extra={
            "success": result.get("success"),
            "execution_time_ms": result.get("execution_time_ms")
        }
    )
    
    return result


@mcp.tool()
async def query_metrics(
    service_name: str = "all",
    metric_type: str = "all",
    time_range: str = "15m"
) -> Dict[str, Any]:
    """
    Query system metrics like CPU usage, memory, latency, and error rates.
    
    Use this to understand system performance and resource utilization.
    
    Args:
        service_name: Name of the service to query or 'all' for all services
        metric_type: Type of metric to query (cpu, memory, latency, error_rate, all)
        time_range: Time range to query (5m, 15m, 30m, 1h, 3h, 24h)
    
    Returns:
        Dictionary containing time-series metric data points
    """
    logger.info(
        "MCP tool called: query_metrics",
        extra={
            "service_name": service_name,
            "metric_type": metric_type,
            "time_range": time_range
        }
    )
    
    result = await metrics_tool.run(
        service_name=service_name,
        metric_type=metric_type,
        time_range=time_range
    )
    
    logger.info(
        "query_metrics completed",
        extra={
            "success": result.get("success"),
            "execution_time_ms": result.get("execution_time_ms")
        }
    )
    
    return result


@mcp.resource("config://settings")
def get_server_config() -> Dict[str, Any]:
    """
    Get current server configuration.
    
    Returns server settings like environment, mock data status, etc.
    """
    return {
        "environment": settings.environment,
        "use_mock_data": settings.use_mock_data,
        "gcp_project": settings.google_cloud_project if settings.google_cloud_project else "not configured",
        "gcp_region": settings.gcp_region,
        "openai_model": settings.openai_model
    }


@mcp.resource("status://health")
def get_health_status() -> Dict[str, str]:
    """
    Get server health status.
    
    Returns basic health check information.
    """
    return {
        "status": "healthy",
        "service": "incident-intelligence-mcp",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    logger.info("Starting MCP Server for Incident Intelligence")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Mock data mode: {settings.use_mock_data}")
    
    mcp.run()

