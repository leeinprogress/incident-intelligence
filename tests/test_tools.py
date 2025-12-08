import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from src.mcp_tools.logs_tool import LogsQueryTool
from src.mcp_tools.metrics_tool import MetricsQueryTool


class TestMetricsQueryTool:
    
    @pytest.fixture
    def metrics_tool(self):
        return MetricsQueryTool()
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_params(self, metrics_tool):
        result = await metrics_tool.execute(
            service_name="test-service",
            metric_type="all",
            time_range="15m"
        )
        
        assert result["service"] == "test-service"
        assert result["time_range"] == "15m"
        assert result["data_points"] == 15
        assert len(result["metrics"]) == 4  # cpu, memory, latency, error_rate
    
    @pytest.mark.asyncio
    async def test_invalid_time_range_raises_error(self, metrics_tool):
        with pytest.raises(ValueError, match="Invalid time_range"):
            await metrics_tool.execute(time_range="10m")
    
    @pytest.mark.asyncio
    async def test_invalid_time_range_format(self, metrics_tool):
        with pytest.raises(ValueError, match="Invalid time_range"):
            await metrics_tool.execute(time_range="invalid")
    
    @pytest.mark.asyncio
    async def test_empty_time_range(self, metrics_tool):
        with pytest.raises(ValueError, match="Invalid time_range"):
            await metrics_tool.execute(time_range="")
    
    @pytest.mark.asyncio
    async def test_unsupported_metric_type_returns_empty(self, metrics_tool):
        result = await metrics_tool.execute(metric_type="invalid_type")
        
        assert result["metrics"] == {}
    
    @pytest.mark.asyncio
    async def test_metric_type_case_sensitivity(self, metrics_tool):
        result = await metrics_tool.execute(metric_type="CPU")
        
        assert result["metrics"] == {}
    
    @pytest.mark.asyncio
    async def test_minimum_time_range(self, metrics_tool):
        result = await metrics_tool.execute(time_range="5m")
        
        assert result["data_points"] == 5
        assert len(result["metrics"]["cpu_usage_percent"]) == 5
    
    @pytest.mark.asyncio
    async def test_maximum_time_range(self, metrics_tool):
        result = await metrics_tool.execute(time_range="24h")
        
        assert result["data_points"] == 1440
        assert len(result["metrics"]["cpu_usage_percent"]) == 1440
    
    @pytest.mark.asyncio
    async def test_timeseries_no_negative_values(self, metrics_tool):
        result = await metrics_tool.execute(metric_type="all", time_range="15m")
        
        for metric_name, data_points in result["metrics"].items():
            for point in data_points:
                assert point["value"] >= 0, f"Negative value found in {metric_name}"
    
    @pytest.mark.asyncio
    async def test_timeseries_valid_timestamps(self, metrics_tool):
        result = await metrics_tool.execute(time_range="5m")
        
        for data_points in result["metrics"].values():
            for point in data_points:
                datetime.fromisoformat(point["timestamp"])
    
    @pytest.mark.asyncio
    async def test_run_wrapper_handles_exception(self, metrics_tool):
        with patch.object(metrics_tool, 'execute', side_effect=RuntimeError("Mock error")):
            result = await metrics_tool.run()
            
            assert result["success"] is False
            assert "error" in result
            assert "Mock error" in result["error"]
            assert "execution_time_ms" in result
            assert "timestamp" in result
    


class TestLogsQueryTool:
    
    @pytest.fixture
    def logs_tool(self):
        return LogsQueryTool()
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_params(self, logs_tool):
        result = await logs_tool.execute(
            service_name="checkout-service",
            severity="error",
            time_range="15m",
            limit=50
        )
        
        assert "logs" in result
        assert "total_logs" in result
        assert result["service"] == "checkout-service"
        assert len(result["logs"]) <= 50
    
    @pytest.mark.asyncio
    async def test_invalid_time_range_raises_error(self, logs_tool):
        with pytest.raises(ValueError, match="Invalid time_range"):
            await logs_tool.execute(time_range="invalid")
    
    @pytest.mark.asyncio
    async def test_invalid_severity_returns_empty_or_all(self, logs_tool):
        result = await logs_tool.execute(severity="invalid_severity")
        
        for log in result["logs"]:
            assert "severity" in log
    
    @pytest.mark.asyncio
    async def test_negative_limit_behavior(self, logs_tool):
        result = await logs_tool.execute(limit=-1)
        
        assert isinstance(result["logs"], list)
    
    @pytest.mark.asyncio
    async def test_severity_case_sensitivity(self, logs_tool):
        result = await logs_tool.execute(severity="ERROR")
        
        for log in result["logs"]:
            assert log["severity"].lower() == "error"

    @pytest.mark.asyncio
    async def test_zero_limit(self, logs_tool):
        result = await logs_tool.execute(limit=0)
        
        assert len(result["logs"]) == 0
    
    @pytest.mark.asyncio
    async def test_limit_one(self, logs_tool):
        result = await logs_tool.execute(limit=1)
        
        assert len(result["logs"]) <= 1
    
    @pytest.mark.asyncio
    async def test_very_large_limit(self, logs_tool):
        result = await logs_tool.execute(limit=10000)
        
        assert len(result["logs"]) <= 10000
        assert isinstance(result["logs"], list)
    
    @pytest.mark.asyncio
    async def test_severity_filtering_strict(self, logs_tool):
        result = await logs_tool.execute(severity="critical")
        
        for log in result["logs"]:
            assert log["severity"].lower() == "critical"
    
    @pytest.mark.asyncio
    async def test_all_severity_filter(self, logs_tool):
        result = await logs_tool.execute(severity="all")
        
        severities = set(log["severity"] for log in result["logs"])
        assert len(severities) >= 1
    
    @pytest.mark.asyncio
    async def test_log_structure_validity(self, logs_tool):
        result = await logs_tool.execute(limit=5)
        
        required_fields = ["timestamp", "severity", "service", "message", "trace_id"]
        
        for log in result["logs"]:
            for field in required_fields:
                assert field in log, f"Log missing required field: '{field}'"
            
            datetime.fromisoformat(log["timestamp"])
    
    @pytest.mark.asyncio
    async def test_run_wrapper_handles_exception(self, logs_tool):
        with patch.object(logs_tool, 'execute', side_effect=RuntimeError("Mock error")):
            result = await logs_tool.run()
            
            assert result["success"] is False
            assert "error" in result
            assert "Mock error" in result["error"]
            assert "execution_time_ms" in result
            assert "timestamp" in result