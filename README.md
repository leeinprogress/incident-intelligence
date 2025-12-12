# Incident Intelligence

Incident diagnosis agent that analyzes production logs and metrics through natural language queries.

**Production API**: https://incident-intelligence-84343680734.asia-northeast3.run.app

**Swagger UI**: https://incident-intelligence-84343680734.asia-northeast3.run.app/docs

```bash
curl -X POST "https://incident-intelligence-84343680734.asia-northeast3.run.app/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is the checkout service slow?"}'
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FastAPI Server                      │
│                    (Async/Await)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   DiagnosisAgent      │
         │   (ReAct Pattern)     │
         └───────────┬───────────┘
                     │
          ┌──────────┴──────────┐
          │  OpenAI Function    │
          │  Calling (GPT-4)    │
          └──────────┬──────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│  Logs Tool    │         │ Metrics Tool │
│  (Dual-Mode)  │         │ (Dual-Mode)  │
└───────┬───────┘         └──────┬───────┘
        │                        │
        └────────┬───────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        ▼                  ▼
┌──────────────┐   ┌─────────────┐
│  Mock Data   │   │ GCP Cloud   │
│              │   │ Logging &   │
│              │   │ Monitoring  │
└──────────────┘   └─────────────┘
```

## Technical Highlights

**ReAct Pattern (Reasoning + Acting)**
- Multi-turn conversation with OpenAI Function Calling
- Autonomous tool orchestration with loop prevention
- Self-correcting execution flow

**Async/Await Design**
- FastAPI async handlers for concurrent requests
- Non-blocking tool execution
- Sequential and parallel tool invocation support

**Dual-Mode Operations**
- Mock mode for testing and development
- Real mode with GCP Cloud Logging & Monitoring
- Automatic fallback with graceful error handling

## Tech Stack

- **AI**: OpenAI GPT-4 (Function Calling)
- **Framework**: FastAPI + Uvicorn
- **Runtime**: Python 3.11+
- **Infrastructure**: GCP Cloud Run
- **Observability**: GCP Cloud Logging & Monitoring

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd incident-intelligence

# Configure environment
cp env.example .env
# Add your OPENAI_API_KEY to .env

# Run with Docker
docker compose up

# Or run locally
pip install -r requirements.txt
uvicorn src.main:app --reload
```

**API Documentation**: Visit `/docs` for interactive Swagger UI

## API Endpoints

- `POST /api/v1/diagnose` - Diagnose incidents with AI
- `GET /api/v1/tools` - List available diagnostic tools
- `GET /health` - Service health check

## License

MIT
