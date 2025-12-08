from google.cloud import logging as gcp_logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Any
import random

from src.mcp_tools.base import BaseTool
from src.config import settings
from src.utils.time_utils import parse_time_range
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LogsQueryTool(BaseTool):
    """
    Query and analyze application logs from various services.

    Supports filtering by service name, time range, and severity level.
    Returns structured log entries with timestamps and trace IDs.
    """

    def __init__(self):
        super().__init__(name="logs_query")

        if not settings.use_mock_data and settings.google_cloud_project:
            try:
                self.gcp_client = gcp_logging.Client(project=settings.google_cloud_project)
                self.gcp_client.setup_logging()
                logger.info(f"GCP Logging client initialized for project: {settings.google_cloud_project}")
            except Exception as e:
                logger.error(f"Failed to initialize GCP Logging client: {e}")
                logger.warning("Falling back to mock mode - will use mock data even if use_mock_data=False")
                self.gcp_client = None
        else:
            self.gcp_client = None

    
    # ============================================================
    # Public Interface
    # ============================================================

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
        
        if settings.use_mock_data or not self.gcp_client:
            # Use mock data if explicitly requested OR if GCP client failed to initialize
            if not settings.use_mock_data and not self.gcp_client:
                logger.warning("GCP client not available, using mock data instead")
            return self._generate_mock_logs(service_name, time_range, severity, limit)
        else:
            return self._query_gcp_logs(service_name, time_range, severity, limit)


    # ============================================================
    # GCP Data Source
    # ============================================================

    def _query_gcp_logs(self,
        service_name: str,
        time_range: str,
        severity: str,
        limit: int
    ) -> Dict[str, Any]:
        """
        Query real GCP Cloud Logging
        """
        minutes = parse_time_range(time_range)
        time_ago = datetime.now(UTC) - timedelta(minutes=minutes)
        
        filters = [
            'resource.type="cloud_run_revision"', 
            f'timestamp>="{time_ago.isoformat()}"'  
        ]
        
        if service_name != "all":
            filters.append(f'labels.service="{service_name}"')
        
        if severity != "all":
            severity_map = {
                "info": "INFO",
                "warning": "WARNING",
                "error": "ERROR",
                "critical": "CRITICAL"
            }
            gcp_severity = severity_map.get(severity.lower(), "INFO")
            filters.append(f'severity>="{gcp_severity}"')
        
        filter_str = " AND ".join(filters)


        logs = []
        try:
            for entry in self.gcp_client.list_entries(
                filter_=filter_str,
                max_results=limit,
                order_by=gcp_logging.DESCENDING  
            ):
                logs.append({
                    "timestamp": entry.timestamp.isoformat() if entry.timestamp else datetime.now(UTC).isoformat(),
                    "severity": entry.severity or "INFO",
                    "service": service_name,
                    "message": str(entry.payload) if entry.payload else "",
                    "trace_id": entry.trace or "N/A"
                })
        
        except Exception as e:
            raise RuntimeError(f"Failed to query GCP logs: {str(e)}") from e
        
        return {
            "total_logs": len(logs),
            "time_range": time_range,
            "service": service_name,
            "logs": logs
        }


    # ============================================================
    # Mock Data Source
    # ============================================================

    def _generate_mock_logs(
        self,
        service_name: str,
        time_range: str, 
        severity: str,
        limit: int
    ) -> Dict[str, Any]:
        """Generate realistic mock log data"""

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
        

        filtered_templates = [
            t for t in log_templates
            if (service_name == "all" or t["service"] == service_name)
            and (severity == "all" or t["severity"].lower() == severity.lower())
        ]


        num_logs = min(random.randint(10, 50), limit)
        for i in range(num_logs):
            template = random.choice(filtered_templates) if filtered_templates else log_templates[0]
            
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