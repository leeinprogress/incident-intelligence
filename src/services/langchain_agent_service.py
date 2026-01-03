"""
LangChain-based Diagnosis Agent

This module implements the same incident diagnosis logic as agent_service.py
but uses LangChain for LLM integration instead of direct OpenAI API calls.

Key differences from agent_service.py:
- Uses ChatOpenAI instead of AsyncOpenAI
- Uses .bind_tools() instead of manual function schemas
- Tool execution remains the same (reuses existing tools)
- ReAct pattern implementation is nearly identical

This allows for direct comparison between:
- OpenAI direct API (agent_service.py)
- LangChain framework (this file)
"""

from typing import Dict, Any, Optional
from datetime import datetime, UTC
import uuid
import json

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from src.config import settings
from src.tools.langchain_tools import tools
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LangChainDiagnosisAgent:
    """
    AI Agent that diagnoses incidents using LangChain
    
    Architecture:
    - LangChain ChatOpenAI for LLM integration
    - LangChain StructuredTools for tool definitions
    - Manual ReAct loop (similar to original agent)
    - Async execution throughout
    
    Usage:
        agent = LangChainDiagnosisAgent()
        result = await agent.diagnose(
            query="Why is checkout-service slow?",
            service_name="checkout-service",
            time_range="15m"
        )
    """
    
    def __init__(self):
        """Initialize LangChain agent with LLM and tools"""
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Bind tools to LLM (LangChain handles schema conversion)
        self.llm_with_tools = self.llm.bind_tools(tools)
        
        # Tool registry (name -> tool instance)
        self.tools_dict = {tool.name: tool for tool in tools}
        
        logger.info("LangChainDiagnosisAgent initialized")
    
    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given input
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
        """
        tool = self.tools_dict.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        logger.info(f"Executing LangChain tool: {tool_name}", extra={"tool_input": tool_input})
        
        # Execute tool (async)
        result = await tool.ainvoke(tool_input)
        
        logger.info(
            f"LangChain tool {tool_name} completed",
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
        Diagnose an incident using LangChain agent
        
        Args:
            query: User's question about the incident
            service_name: Optional service name to focus on
            time_range: Time range for analysis (5m, 15m, 30m, 1h, 3h, 24h)
            
        Returns:
            Diagnosis result with analysis, tools executed, and metadata
        """
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(UTC)
        
        logger.info(f"Starting LangChain diagnosis: {request_id}", extra={"query": query})
        
        # Build system prompt
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
        
        # Initialize conversation messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]
        
        # Track tool executions
        tool_executions = []
        final_response = None
        max_iterations = 5  # Prevent infinite loops
        
        # ReAct loop
        for iteration in range(max_iterations):
            logger.info(f"LangChain iteration {iteration + 1}/{max_iterations}")
            
            # Call LLM with tools
            response = await self.llm_with_tools.ainvoke(messages)
            
            # Check if LLM wants to call tools
            if not response.tool_calls:
                # LLM has finished analysis
                final_response = response.content
                break
            
            # Add LLM's response to conversation
            messages.append(response)
            
            # Execute all tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                
                logger.info(f"LLM requested tool: {tool_name}", extra={"tool_input": tool_input})
                
                # Execute tool
                tool_result = await self._execute_tool(tool_name, tool_input)
                
                # Record execution for response
                tool_executions.append({
                    "tool_name": tool_name,
                    "execution_time_ms": tool_result.get("execution_time_ms", 0),
                    "result_summary": self._summarize_tool_result(tool_name, tool_result),
                    "data_points": self._count_data_points(tool_result)
                })
                
                # Add tool result to conversation
                tool_message = ToolMessage(
                    content=json.dumps(tool_result.get("data", {})),
                    tool_call_id=tool_call["id"]
                )
                messages.append(tool_message)
        
        # Check if analysis was completed
        if final_response is None:
            final_response = "Analysis incomplete: maximum tool call iterations reached."
            logger.warning(f"Max iterations reached for request {request_id}")
        
        # Calculate processing time
        processing_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        
        # Build diagnosis result
        diagnosis_result = {
            "request_id": request_id,
            "status": "success",
            "query": query,
            "analysis": final_response,
            "tools_executed": tool_executions,
            "processing_time_ms": processing_time,
            "timestamp": datetime.now(UTC).isoformat(),
            "framework": "langchain"  # Identifier for comparison
        }
        
        logger.info(
            f"LangChain diagnosis complete: {request_id}",
            extra={"processing_time_ms": processing_time}
        )
        
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

