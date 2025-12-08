import pytest
from unittest.mock import AsyncMock, patch
from src.models.response import DiagnosisResponse, ToolExecution


class TestHealthCheck:
    def test_health_check(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGetTools:
    def test_get_tools(self, client):
        response = client.get("/api/v1/tools")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert len(data["tools"]) == 2
        assert data["tools"][0]["name"] == "query_logs"
        assert data["tools"][0]["description"] == "Query application logs to find errors, warnings, and events"
        assert data["tools"][1]["name"] == "query_metrics"
        assert data["tools"][1]["description"] == "Query system metrics (CPU, memory, latency, error rates)"


class TestDiagnose:
    
    @pytest.fixture
    def mock_agent_response(self):
        return DiagnosisResponse(
            request_id="test_req_123",
            status="success",
            query="Why is the checkout service slow?",
            analysis="The checkout service is slow because the database connection pool is exhausted.",
            tools_executed=[
                ToolExecution(
                    tool_name="query_logs",
                    execution_time_ms=125,
                    result_summary="Found 25 logs",
                    data_points=25
                ),
                ToolExecution(
                    tool_name="query_metrics",
                    execution_time_ms=89,
                    result_summary="Retrieved 4 metric types",
                    data_points=15
                )
            ],
            processing_time_ms=3245,
            timestamp="2024-12-06T10:50:30.123456Z"
        )
    
    def test_diagnose_with_valid_request(self, client, mock_agent_response):
        with patch('src.main.agent.diagnose', new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = mock_agent_response
            
            response = client.post("/api/v1/diagnose", json={
                "query": "Why is the checkout service slow?",
                "service_name": "checkout-service",
                "time_range": "15m"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["request_id"] == "test_req_123"
            assert data["status"] == "success"
            assert data["query"] == "Why is the checkout service slow?"
            assert "analysis" in data
            assert len(data["tools_executed"]) == 2
            assert data["processing_time_ms"] > 0
            assert "timestamp" in data
            
            mock_diagnose.assert_called_once_with(
                query="Why is the checkout service slow?",
                service_name="checkout-service",
                time_range="15m"
            )
    
    def test_diagnose_with_minimal_request(self, client, mock_agent_response):
        with patch('src.main.agent.diagnose', new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = mock_agent_response
            
            response = client.post("/api/v1/diagnose", json={
                "query": "System is slow"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    def test_diagnose_response_structure(self, client, mock_agent_response):
        with patch('src.main.agent.diagnose', new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = mock_agent_response
            
            response = client.post("/api/v1/diagnose", json={
                "query": "Test query"
            })
            
            data = response.json()
            
            required_fields = [
                "request_id", "status", "query", "analysis",
                "tools_executed", "processing_time_ms", "timestamp"
            ]
            
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            for tool in data["tools_executed"]:
                assert "tool_name" in tool
                assert "execution_time_ms" in tool
                assert "result_summary" in tool
                assert "data_points" in tool
