from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import random

from src.mcp_tools.base import BaseTool
from src.config import settings
from src.utils.time_utils import parse_time_range


class MetricsQueryTool(BaseTool):
    """
    Query and analyze system metrics (CPU, memory, latency, error rates).
    
    Returns time-series data points for requested metrics within specified
    time range. Supports filtering by service and metric type.
    """

    def __init__(self):
        super().__init__(name="metrics_query")

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


        if settings.use_mock_data:
            return self._generate_mock_metrics(service_name, metric_type, time_range)
        else:
            raise NotImplementedError("Real GCP metrics integration will be implemented")


    def _generate_mock_metrics(
        self,
        service_name: str,
        metric_type: str,
        time_range: str
    ) -> Dict[str, Any]:
        """Generate realistic mock metrics data"""
        
        # Parse time range
        minutes = parse_time_range(time_range)
        # Number of data points (one per minute)
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
            
            # Base value with random fluctuation
            value = base + random.uniform(-variance, variance)
            
            # Occasionally create spikes (simulating problems)
            if random.random() < spike_prob:
                value *= spike_magnitude
            
            # Prevent negative values
            value = max(0, value)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "value": round(value, 2)
            })
        
        return data
