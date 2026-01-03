from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import random
import asyncio
from datetime import datetime, UTC

from src.utils.logger import setup_logging, get_logger
from src.services.agent_service import DiagnosisAgent
from src.services.langchain_agent_service import LangChainDiagnosisAgent
from src.models.request import IncidentQuery
from src.models.response import DiagnosisResponse


setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Incident Intelligence Platform", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize both agents for comparison
agent = DiagnosisAgent()  # OpenAI direct
langchain_agent = LangChainDiagnosisAgent()  # LangChain framework


@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/diagnose", response_model=DiagnosisResponse)
async def diagnose(query: IncidentQuery):
    """
    Diagnose incidents using OpenAI Function Calling (direct API)
    
    This endpoint uses the original implementation with direct OpenAI API calls.
    """
    try: 
        logger.info(f"Diagnosis request received (OpenAI)", extra={"query": query.query})
        result = await agent.diagnose(
            query = query.query,
            service_name = query.service_name,
            time_range = query.time_range
        )
        return result
    except Exception as e:
        logger.error(f"Error diagnosing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/diagnose-langchain", response_model=DiagnosisResponse)
async def diagnose_langchain(query: IncidentQuery):
    """
    Diagnose incidents using LangChain framework
    
    This endpoint uses LangChain's ChatOpenAI and StructuredTools for the same diagnosis logic.
    Allows for direct comparison with the OpenAI direct implementation.
    
    Response includes 'framework': 'langchain' field for identification.
    """
    try:
        logger.info(f"Diagnosis request received (LangChain)", extra={"query": query.query})
        result = await langchain_agent.diagnose(
            query=query.query,
            service_name=query.service_name,
            time_range=query.time_range
        )
        return result
    except Exception as e:
        logger.error(f"Error diagnosing incident (LangChain): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tools")
def get_tools():
    return {
        "tools": [
            {
                "name": "query_logs",
                "description": "Query application logs to find errors, warnings, and events"
            },
            {
                "name": "query_metrics",
                "description": "Query system metrics (CPU, memory, latency, error rates)"
            }
        ]
    }


@app.post("/simulate/db-exhaustion", tags=["simulation"])
async def simulate_db_exhaustion():
    """
    Simulate database connection pool exhaustion
    
    Generates realistic error logs:
    - Multiple connection pool exhaustion errors
    - Critical out of memory error
    - Simulates slow response time
    """
    start_time = time.time()
    trace_id = f"trace_{random.randint(10000, 99999)}"
    scenario = "db-exhaustion"
    
    # Connection pool exhaustion errors
    for i in range(5):
        logger.error(
            "Database connection pool exhausted: max_connections=100, active=100",
            extra={
                "service": "checkout-service", 
                "scenario": scenario,
                "attempt": i+1,
                "trace_id": trace_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
        await asyncio.sleep(0.2) 
    
    # Critical memory issue
    logger.critical(
        "Out of memory: heap usage 98%, triggering garbage collection",
        extra={
            "service": "checkout-service",
            "scenario": scenario,
            "trace_id": trace_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
    
    # Simulate slow response time
    delay = random.uniform(2, 4)
    await asyncio.sleep(delay)
    
    return {
        "status": "simulated",
        "scenario": scenario,
        "logs_generated": 6,
        "trace_id": trace_id,
        "duration_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.now(UTC).isoformat()
    }


@app.post("/simulate/high-latency", tags=["simulation"])
async def simulate_high_latency():
    """
    Simulate high latency issues
    
    Generates warning logs showing degraded performance:
    - Multiple high latency warnings (3-8s response times)
    - Simulates slow endpoint responses
    """
    start_time = time.time()
    trace_id = f"trace_{random.randint(10000, 99999)}"
    scenario = "high-latency"
    
    # Generate high latency warnings
    for i in range(3):
        latency = random.uniform(3, 8)
        logger.warning(
            f"High latency detected: response_time={latency:.1f}s (threshold: 1s)",
            extra={
                "service": "checkout-service",
                "scenario": scenario,
                "trace_id": trace_id,
                "latency_ms": int(latency * 1000),
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
        await asyncio.sleep(0.5)
    
    # Simulate actual slow response
    delay = random.uniform(3, 5)
    await asyncio.sleep(delay)
    
    return {
        "status": "simulated",
        "scenario": scenario,
        "logs_generated": 3,
        "trace_id": trace_id,
        "duration_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.now(UTC).isoformat()
    }


@app.post("/simulate/memory-leak", tags=["simulation"])
async def simulate_memory_leak():
    """
    Simulate memory leak warnings
    
    Generates progressive memory usage warnings:
    - Gradual increase from 75% to 95%
    - Critical memory leak alert
    - Simulates actual memory allocation
    """
    start_time = time.time()
    trace_id = f"trace_{random.randint(10000, 99999)}"
    scenario = "memory-leak"
    
    # Progressive memory increase simulation
    memory_percentages = [75, 82, 89, 95]
    for mem_pct in memory_percentages:
        logger.warning(
            f"Memory usage increasing: {mem_pct}% of heap used",
            extra={
                "service": "payment-service",
                "scenario": scenario,
                "trace_id": trace_id,
                "memory_percent": mem_pct,
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
        await asyncio.sleep(0.3)
    
    # Critical alert
    logger.critical(
        "Memory usage critical: 95% of heap used - potential memory leak detected",
        extra={
            "service": "payment-service",
            "scenario": scenario,
            "trace_id": trace_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
    
    # Simulate memory usage (GC will clean up)
    waste = [0] * 1000000
    del waste
    
    return {
        "status": "simulated",
        "scenario": scenario,
        "logs_generated": 5,
        "trace_id": trace_id,
        "duration_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.now(UTC).isoformat()
    }


@app.post("/simulate/multi-issue", tags=["simulation"])
async def simulate_multi_issue():
    """
    Simulate multiple issues at once (realistic scenario)
    
    Generates mixed severity logs representing complex incident:
    - Database connection errors
    - High latency warnings
    - Memory usage warnings
    - Normal operation logs (to add realism)
    """
    start_time = time.time()
    trace_id = f"trace_{random.randint(10000, 99999)}"
    scenario = "multi-issue"
    logs_count = 0
    
    # Database error
    logger.error(
        "Failed to acquire database connection: timeout after 30s",
        extra={
            "service": "checkout-service",
            "scenario": scenario,
            "trace_id": trace_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
    logs_count += 1
    await asyncio.sleep(0.2)
    
    # High latency warning
    logger.warning(
        "High latency detected: response_time=5.2s",
        extra={
            "service": "checkout-service",
            "scenario": scenario,
            "trace_id": trace_id,
            "latency_ms": 5200,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
    logs_count += 1
    await asyncio.sleep(0.2)
    
    # Memory warning
    logger.warning(
        "Memory usage high: 85% of heap used",
        extra={
            "service": "payment-service",
            "scenario": scenario,
            "trace_id": trace_id,
            "memory_percent": 85,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
    logs_count += 1
    
    # Normal operation logs (mixed with errors for realism)
    for i in range(10):
        logger.info(
            f"Successfully processed request: request_id=req_{random.randint(1000, 9999)}",
            extra={
                "service": random.choice(["checkout-service", "payment-service"]),
                "scenario": scenario,
                "trace_id": f"trace_{random.randint(10000, 99999)}",
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
        logs_count += 1
        await asyncio.sleep(0.1)
    
    return {
        "status": "simulated",
        "scenario": scenario,
        "logs_generated": logs_count,
        "trace_id": trace_id,
        "duration_ms": int((time.time() - start_time) * 1000),
        "timestamp": datetime.now(UTC).isoformat()
    }


