from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
import uuid
import json
from openai import AsyncOpenAI
from src.config import settings
from src.mcp_tools import LogsQueryTool, MetricsQueryTool
from src.utils.logger import get_logger


logger = get_logger(__name__)



class DiagnosisAgent:
    """
    AI Agent that diagnoses incidents using MCP tools
    
    The agent uses OpenAI's function calling to:
    1. Analyze user queries about incidents
    2. Automatically decide which tools to use (logs, metrics)
    3. Execute tools and collect data
    4. Synthesize results into actionable diagnosis
    """


    def __init__(self):
        # OpenAI client
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

        # MCP tools
        self.logs_tool = LogsQueryTool()
        self.metrics_tool = MetricsQueryTool()

        # Tool registry (name -> tool instance)
        self.tools = {
            "query_logs": self.logs_tool,
            "query_metrics": self.metrics_tool
        }

        # OpenAI Function definitions
        self.function_schemas = self._build_function_schemas()

        logger.info("DiagnosisAgent initialized")

    def _build_function_schemas(self) -> List[Dict[str, Any]]:
        """
        Build OpenAI function schemas from MCP tools
        
        This converts our MCP tools into a format that OpenAI understands.
        LLM will use these schemas to decide when and how to call tools.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_logs",
                    "description": "Query application logs to find errors, warnings, and events. Use this to investigate what happened in the system.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Name of the service to query (e.g., 'checkout-service', 'payment-service') or 'all' for all services",
                                "default": "all"
                            },
                            "time_range": {
                                "type": "string",
                                "enum": ["5m", "15m", "30m", "1h", "3h", "24h"],
                                "description": "Time range to query",
                                "default": "15m"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["info", "warning", "error", "critical", "all"],
                                "description": "Log severity level to filter",
                                "default": "all"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of logs to return",
                                "default": 100
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_metrics",
                    "description": "Query system metrics like CPU usage, memory, latency, and error rates. Use this to understand system performance and resource utilization.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Name of the service to query or 'all' for all services",
                                "default": "all"
                            },
                            "metric_type": {
                                "type": "string",
                                "enum": ["cpu", "memory", "latency", "error_rate", "all"],
                                "description": "Type of metric to query",
                                "default": "all"
                            },
                            "time_range": {
                                "type": "string",
                                "enum": ["5m", "15m", "30m", "1h", "3h", "24h"],
                                "description": "Time range to query",
                                "default": "15m"
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
        
        Returns:
            Tool execution result
        """
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        logger.info(f"Executing tool: {tool_name}", extra={"arguments": arguments})
        
        # Execute the tool
        result = await tool.run(**arguments)
        
        logger.info(
            f"Tool {tool_name} completed",
            extra={"success": result.get("success"), "execution_time": result.get("execution_time_ms")}
        )
        
        return result

    async def diagnose(
        self,
        query: str,
        service_name: Optional[str] = None,
        time_range: str = "15m"
    ) -> Dict[str, Any]:
        """
        Diagnose an incident using LLM and MCP tools
        
        Args:
            query: User's question about the incident
            service_name: Optional service name to focus on
            time_range: Time range for analysis
        
        Returns:
            Diagnosis result with root cause, affected services, and suggestions
        """
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(UTC)
        
        logger.info(f"Starting diagnosis: {request_id}", extra={"query": query})
        
        # Build initial system prompt
        system_prompt = f"""You are an expert SRE (Site Reliability Engineer) diagnosing production incidents.

Your role:
1. Analyze the user's question about an incident
2. Use available tools (query_logs, query_metrics) to gather data
3. Identify root causes, affected services, and timeline
4. Provide actionable remediation suggestions

Context:
- Service: {service_name or "all services"}
- Time range: {time_range}

Be thorough but concise. Focus on actionable insights."""

        # Conversation messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        # Tool execution results
        tool_executions = []
        final_response = None
        max_iterations = 5  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            logger.info(f"LLM iteration {iteration + 1}/{max_iterations}")
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=self.function_schemas,
                temperature=settings.openai_temperature
            )
            
            assistant_message = response.choices[0].message
            
            # Check if LLM wants to call tools
            if not assistant_message.tool_calls:
                # LLM has finished analysis
                final_response = assistant_message.content
                break
            
            # Add assistant's message to conversation
            messages.append(assistant_message)
            
            # Execute all tool calls
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"LLM requested tool: {function_name}", extra={"args": function_args})
                
                # Execute tool
                tool_result = await self._execute_tool(function_name, function_args)
                
                # Record execution
                tool_executions.append({
                    "tool_name": function_name,
                    "execution_time_ms": tool_result.get("execution_time_ms", 0),
                    "result_summary": self._summarize_tool_result(function_name, tool_result),
                    "data_points": self._count_data_points(tool_result)
                })
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result.get("data", {}))
                })
        
        # Check if analysis was completed
        if final_response is None:
            final_response = "Analysis incomplete: maximum tool call iterations reached."
            logger.warning(f"Max iterations reached for request {request_id}")
        
        # Calculate processing time
        processing_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        
        # Parse final response (simple version for Day 1)
        diagnosis_result = {
            "request_id": request_id,
            "status": "success",
            "query": query,
            "analysis": final_response,
            "tools_executed": tool_executions,
            "processing_time_ms": processing_time,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        logger.info(f"Diagnosis complete: {request_id}", extra={"processing_time_ms": processing_time})
        
        return diagnosis_result


    def _summarize_tool_result(self, tool_name: str, result: Dict) -> str:
        """Create a brief summary of tool execution result"""
        if not result.get("success"):
            return f"Error: {result.get('error', 'Unknown error')}"
        
        data = result.get("data", {})
        
        if tool_name == "query_logs":
            return f"Found {data.get('total_logs', 0)} logs"
        elif tool_name == "query_metrics":
            metrics_count = len(data.get("metrics", {}))
            return f"Retrieved {metrics_count} metric types"
        
        return "Executed successfully"
    
    def _count_data_points(self, result: Dict) -> int:
        """Count data points in tool result"""
        if not result.get("success"):
            return 0
        
        data = result.get("data", {})
        
        if "total_logs" in data:
            return data.get("total_logs", 0)
        elif "data_points" in data:
            return data.get("data_points", 0)
        
        return 0