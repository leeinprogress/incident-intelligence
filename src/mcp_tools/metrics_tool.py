from google.cloud import monitoring_v3
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import random

from src.mcp_tools.base import BaseTool
from src.config import settings
from src.utils.time_utils import parse_time_range
from src.utils.logger import get_logger

logger = get_logger(__name__)



class MetricsQueryTool(BaseTool):
    """
    Query and analyze system metrics (CPU, memory, latency, error rates).
    
    Returns time-series data points for requested metrics within specified
    time range. Supports filtering by service and metric type.
    """

    def __init__(self):
        super().__init__(name="metrics_query")

        if not settings.use_mock_data and settings.google_cloud_project:
            try:
                self.gcp_client = monitoring_v3.MetricServiceClient()
                self.project_name = f"projects/{settings.google_cloud_project}"
                logger.info(f"GCP Monitoring client initialized for project: {settings.google_cloud_project}")
            except Exception as e:
                logger.error(f"Failed to initialize GCP Monitoring client: {e}")
                self.gcp_client = None
        else:
            self.gcp_client = None

    # ============================================================
    # Public Interface
    # ============================================================

    async def execute(
        self,
        service_name: str = "all",
        metric_type: str = "all",
        time_range: str = "15m",
    ) -> Dict[str, Any]:
        """
        Query metrics with filters
        
        Args:
            service_name: Service to query
            metric_type: Type of metric (cpu, memory, latency, error_rate, all)
            time_range: Time range
        
        Returns:
            Dict containing metric data points
        """

        if settings.use_mock_data or not self.gcp_client:
            # Use mock data if explicitly requested OR if GCP client failed to initialize
            if not settings.use_mock_data and not self.gcp_client:
                logger.warning("GCP Monitoring client not available, using mock data instead")
            return self._generate_mock_metrics(service_name, metric_type, time_range)
        else:
            return await self._query_gcp_metrics(service_name, metric_type, time_range)


    # ============================================================
    # GCP Data Source
    # ============================================================

    async def _query_gcp_metrics(
        self,
        service_name: str,
        metric_type: str,
        time_range: str
    ) -> Dict[str, Any]:
        """
        Query real GCP Cloud Monitoring metrics
        
        Uses Cloud Run default metrics:
        - CPU utilization
        - Memory utilization
        - Request latency
        - Error rate
        """
        minutes = parse_time_range(time_range)
        now = datetime.now(UTC)
        time_ago = now - timedelta(minutes=minutes)
        
        metrics_data = {}
        total_points = 0
        
        try:
            metric_types_map = {
                "cpu": "run.googleapis.com/container/cpu/utilizations",
                "memory": "run.googleapis.com/container/memory/utilizations",
                "latency": "run.googleapis.com/request_latencies",
                "error_rate": "run.googleapis.com/request_count"
            }
            
            if metric_type == "all":
                query_metrics = list(metric_types_map.keys())
            else:
                query_metrics = [metric_type] if metric_type in metric_types_map else []
            
            logger.info(f"Querying GCP metrics: {query_metrics} for service: {service_name}, time_range: {time_range}")
            
            for m_type in query_metrics:
                metric_name = metric_types_map.get(m_type)
                if not metric_name:
                    continue
                
            
                interval = monitoring_v3.TimeInterval(
                    {
                        "end_time": now,
                        "start_time": time_ago,
                    }
                )
                

                filter_parts = [f'metric.type="{metric_name}"']
                filter_parts.append('resource.type="cloud_run_revision"')
                
                if service_name != "all":
                    filter_parts.append(f'resource.labels.service_name="{service_name}"')
                
                filter_str = " AND ".join(filter_parts)
                
                request = monitoring_v3.ListTimeSeriesRequest(
                    {
                        "name": self.project_name,
                        "filter": filter_str,
                        "interval": interval,
                        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                    }
                )
                
               
                results = self.gcp_client.list_time_series(request=request)
                
                
                data_points = []
                for result in results:
                    for point in result.points:
                        data_points.append({
                            "timestamp": point.interval.end_time.isoformat(),
                            "value": self._extract_metric_value(point.value, m_type)
                        })
                
                data_points.sort(key=lambda x: x["timestamp"])
                
                data_points = data_points[-minutes:] if len(data_points) > minutes else data_points
                
                key = self._get_metric_key(m_type)
                metrics_data[key] = data_points
                total_points += len(data_points)
                
                logger.info(f"Retrieved {len(data_points)} points for {m_type}")
            
            if not metrics_data:
                logger.warning(f"No metrics found for service: {service_name}, falling back to mock data")
                return self._generate_mock_metrics(service_name, metric_type, time_range)
        
        except Exception as e:
            logger.error(f"Failed to query GCP metrics: {type(e).__name__}: {str(e)}")
            logger.warning("Falling back to mock metrics")
            return self._generate_mock_metrics(service_name, metric_type, time_range)
        
        return {
            "service": service_name,
            "time_range": time_range,
            "metric_type": metric_type,
            "data_points": total_points,
            "metrics": metrics_data
        }
    
    def _extract_metric_value(self, value, metric_type: str) -> float:
        """Extract numeric value from metric point"""
        try:
            if hasattr(value, 'double_value'):
                val = value.double_value
            elif hasattr(value, 'int64_value'):
                val = float(value.int64_value)
            elif hasattr(value, 'distribution_value'):
                val = value.distribution_value.mean
            else:
                logger.warning(f"Unknown value type for {metric_type}: {type(value)}")
                return 0.0
            
            
            if metric_type in ["cpu", "memory"]:
                val = val * 100
            
            elif metric_type == "latency":
                val = val * 1000
            
            return round(val, 2)
        except Exception as e:
            logger.error(f"Error extracting metric value: {e}")
            return 0.0
    
    def _get_metric_key(self, metric_type: str) -> str:
        """Get consistent metric key name"""
        key_map = {
            "cpu": "cpu_usage_percent",
            "memory": "memory_usage_percent",
            "latency": "response_time_ms",
            "error_rate": "error_rate_percent"
        }
        return key_map.get(metric_type, f"{metric_type}_value")


    # ============================================================
    # Mock Data Source
    # ============================================================
    
    def _generate_mock_metrics(
        self,
        service_name: str,
        metric_type: str,
        time_range: str
    ) -> Dict[str, Any]:
        """Generate realistic mock metrics data"""
        
        minutes = parse_time_range(time_range)
        num_points = minutes
        
        metrics = {}
        
        # CPU usage
        if metric_type in ["cpu", "all"]:
            metrics["cpu_usage_percent"] = self._generate_timeseries(
                num_points, base=60, variance=20, spike_prob=0.1
            )
        
        # memory usage
        if metric_type in ["memory", "all"]:
            metrics["memory_usage_percent"] = self._generate_timeseries(
                num_points, base=75, variance=10, spike_prob=0.05
            )
        
        # response time (latency)
        if metric_type in ["latency", "all"]:
            metrics["response_time_ms"] = self._generate_timeseries(
                num_points, base=250, variance=100, spike_prob=0.15, spike_magnitude=3
            )
        
        # error rate
        if metric_type in ["error_rate", "all"]:
            metrics["error_rate_percent"] = self._generate_timeseries(
                num_points, base=0.5, variance=0.3, spike_prob=0.2, spike_magnitude=10
            )
        
        return {
            "service": service_name,
            "time_range": time_range,
            "metric_type": metric_type,
            "data_points": num_points,
            "metrics": metrics
        }
    
    def _generate_timeseries(
        self,
        num_points: int,
        base: float,
        variance: float,
        spike_prob: float = 0.1,
        spike_magnitude: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Generate realistic time series data with occasional spikes

        - base value with fluctuation
        - sometimes spike occurs (simulating problem situations)
        """
        data = []
        current_time = datetime.now(UTC)
        
        for i in range(num_points):
            timestamp = current_time - timedelta(minutes=num_points - i)
            
            value = base + random.uniform(-variance, variance)
            
            if random.random() < spike_prob:
                value *= spike_magnitude
            
            value = max(0, value)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 2)
            })
        
        return data
