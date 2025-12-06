from datetime import datetime, timedelta, UTC
from typing import Dict, Any
import random

from src.mcp_tools.base import BaseTool
from src.config import settings
from src.utils.time_utils import parse_time_range



class LogsQueryTool(BaseTool):
    """
    Query and analyze application logs from various services.

    Supports filtering by service name, time range, and severity level.
    Returns structured log entries with timestamps and trace IDs.
    """

    def __init__(self):
        super().__init__(name="logs_query")

    async def execute(
        self,
        service_name: str = "all",
        time_range: str = "15m",
        severity: str = "all",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query logs with filters

        Args:
            service_name: Service to query (e.g., "checkout-service")
            time_range: Time range to query (e.g., "15m", "1h", "24h")
            severity: Log severity (info, warning, error, critical, all)
            limit: Max number of logs to return

        Returns:
            Dict containing log entries
        """
        
        if settings.use_mock_data:
            return self._generate_mock_logs(service_name, time_range, severity, limit)
        else:
            raise NotImplementedError("Real GCP logging service will be implemented")

    def _generate_mock_logs(
        self,
        service_name: str,
        time_range: str, 
        severity: str,
        limit: int
    ) -> Dict[str, Any]:
        """Generate realistic mock log data"""

        # Parse time range
        minutes = parse_time_range(time_range)

        mock_logs = []
                
        log_templates = [
            {
                "severity": "ERROR",
                "message": "Database connection pool exhausted: max_connections=100, active=100",
                "service": "checkout-service"
            },
            {
                "severity": "WARNING",
                "message": "High latency detected: response_time=5.2s (threshold: 1s)",
                "service": "checkout-service"
            },
            {
                "severity": "ERROR",
                "message": "Failed to acquire database connection: timeout after 30s",
                "service": "payment-service"
            },
            {
                "severity": "INFO",
                "message": "Successfully processed payment: transaction_id=xyz123",
                "service": "payment-service"
            },
            {
                "severity": "CRITICAL",
                "message": "Out of memory: heap usage 98%, triggering garbage collection",
                "service": "checkout-service"
            }
        ]
        
        # filter by service and severity
        filtered_templates = [
            t for t in log_templates
            if (service_name == "all" or t["service"] == service_name)
            and (severity == "all" or t["severity"].lower() == severity.lower())
        ]

        # generate log entries
        num_logs = min(random.randint(10, 50), limit)
        for i in range(num_logs):
            template = random.choice(filtered_templates) if filtered_templates else log_templates[0]
            
            # timestamp from recent to past
            timestamp = datetime.now(UTC) - timedelta(
                minutes=random.uniform(0, minutes)
            )
            
            mock_logs.append({
                "timestamp": timestamp.isoformat(),
                "severity": template["severity"],
                "service": template["service"],
                "message": template["message"],
                "trace_id": f"trace_{random.randint(1000, 9999)}"
            })

        mock_logs.sort(key= lambda x: x["timestamp"], reverse=True)

        return {
            "total_logs": len(mock_logs),
            "time_range": time_range,
            "service": service_name,
            "logs": mock_logs[:limit]
        }