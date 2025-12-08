from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from src.utils.logger import setup_logging, get_logger
from src.services.agent_service import DiagnosisAgent
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

agent = DiagnosisAgent()


@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/diagnose", response_model=DiagnosisResponse)
async def diagnose(query: IncidentQuery):
    try: 
        logger.info(f"Diagnosis request received", extra={"query": query.query})
        result = await agent.diagnose(
            query = query.query,
            service_name = query.service_name,
            time_range = query.time_range
        )
        return result
    except Exception as e:
        logger.error(f"Error diagnosing incident: {str(e)}")
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




