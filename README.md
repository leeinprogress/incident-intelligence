# Incident Intelligence

Incident diagnosis system that analyzes production logs and metrics through natural language queries using **LangChain** and **OpenAI Function Calling**.

**Production API**: https://incident-intelligence-84343680734.asia-northeast3.run.app

**Swagger UI**: https://incident-intelligence-84343680734.asia-northeast3.run.app/docs

## 🚀 Quick Example

```bash
# Using LangChain implementation
curl -X POST "http://localhost:8000/api/v1/diagnose-langchain" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is checkout-service slow?", "time_range": "15m"}'

# Using OpenAI direct implementation
curl -X POST "http://localhost:8000/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"query": "Why is checkout-service slow?", "time_range": "15m"}'
```

## 🏗️ Architecture

### Two Implementation Approaches

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
               ▼                          ▼
    ┌──────────────────┐      ┌──────────────────────┐
    │  DiagnosisAgent  │      │ LangChainDiagnosis   │
    │  (OpenAI Direct) │      │ Agent (LangChain)    │
    └────────┬─────────┘      └──────────┬───────────┘
             │                           │
             ▼                           ▼
    ┌─────────────────┐        ┌──────────────────┐
    │ OpenAI Function │        │  ChatOpenAI +    │
    │ Calling (Raw)   │        │  .bind_tools()   │
    └────────┬────────┘        └──────────┬───────┘
             │                            │
             └──────────┬─────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
      ┌───────────────┐   ┌──────────────┐
      │  query_logs   │   │query_metrics │
      │(LangChain Tool)   │(LangChain Tool)
      └───────┬───────┘   └──────┬───────┘
              │                  │
              └────────┬─────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       ┌─────────┐       ┌──────────┐
       │Mock Data│       │GCP Cloud │
       └─────────┘       └──────────┘
```

## 🧠 LangChain Integration

This project demonstrates **two approaches** to LLM tool integration:

### 1. OpenAI Function Calling (Direct API)
- Raw OpenAI API with manual function schemas
- Full control over request/response
- Lower abstraction, explicit error handling

### 2. LangChain Framework
- `ChatOpenAI` with `.bind_tools()` for automatic schema conversion
- `StructuredTool` with Pydantic validation
- Higher abstraction, cleaner code

### Comparison

| Feature | OpenAI Direct | LangChain |
|---------|--------------|-----------|
| **Abstraction** | Low | High |
| **Control** | Full | Framework-managed |
| **Tool Definition** | Manual JSON schemas | `StructuredTool` + Pydantic |
| **Code Verbosity** | Higher | Lower |
| **Learning Curve** | OpenAI API docs | LangChain + OpenAI |

**Both implementations**:
- Use the same ReAct pattern
- Execute identical tools
- Provide the same diagnosis quality
- Support async operations

## 🎯 Technical Highlights

**ReAct Pattern (Reasoning + Acting)**
- Multi-turn conversation with iterative tool calling
- Autonomous tool orchestration with loop prevention
- Self-correcting execution flow

**LangChain Tools**
- Pydantic schemas for type-safe tool inputs
- Async tool execution with `coroutine` support
- Reusable tool wrappers (no code duplication)

**Dual-Mode Operations**
- Mock mode for testing and development
- Production mode with GCP Cloud Logging & Monitoring
- Graceful fallback on errors

## 🛠️ Tech Stack

- **AI/LLM**: OpenAI GPT-4, LangChain, LangChain-OpenAI
- **Framework**: FastAPI + Uvicorn (async)
- **Runtime**: Python 3.11+
- **Infrastructure**: GCP Cloud Run (serverless)
- **Observability**: GCP Cloud Logging & Monitoring
- **Tools**: Pydantic, StructuredTool

## 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd incident-intelligence

# Using Makefile (recommended)
make install          # Install dependencies
make run              # Run locally
make docker-up        # Run with Docker

# Or manually
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**API Documentation**: Visit `http://localhost:8000/docs` for interactive Swagger UI

## 📡 API Endpoints

| Endpoint | Method | Description | Framework |
|----------|--------|-------------|-----------|
| `/api/v1/diagnose` | POST | Diagnose incidents | OpenAI Direct |
| `/api/v1/diagnose-langchain` | POST | Diagnose incidents | LangChain |
| `/api/v1/tools` | GET | List available tools | - |
| `/` | GET | Health check | - |

### Example Request

```json
{
  "query": "Why is checkout-service experiencing high latency?",
  "service_name": "checkout-service",
  "time_range": "15m"
}
```

### Example Response

```json
{
  "request_id": "req_abc123",
  "status": "success",
  "query": "Why is checkout-service experiencing high latency?",
  "analysis": "The checkout-service is experiencing...",
  "tools_executed": [
    {"tool_name": "query_logs", "execution_time_ms": 150},
    {"tool_name": "query_metrics", "execution_time_ms": 120}
  ],
  "processing_time_ms": 2500,
  "framework": "langchain"
}
```

## License

MIT
