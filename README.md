# Incident Intelligence

> 🚧 **Status**: Early Development

AI agent that diagnoses production incidents by analyzing logs and metrics through natural language queries.

**Example:**
```python
agent = DiagnosisAgent()
result = await agent.diagnose("Why is the checkout service slow?")
# → AI automatically queries logs + metrics and explains root cause
```

## How It Works

1. Ask a question in natural language
2. AI decides which tools to use (logs, metrics)
3. Tools execute and gather data
4. AI synthesizes findings into actionable diagnosis

## Quick Start

**Prerequisites:** Docker & Docker Compose (recommended) OR Python 3.11+
> **Get API Key:** Sign up at [platform.openai.com](https://platform.openai.com) → API keys → Create new key

### Option 1: Docker Compose (Recommended)

```bash
# 1. Set up environment variables
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Run with Docker Compose
docker compose up

# Or run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Option 2: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run test
python -m src.test_agent

# 4. Run API server
uvicorn src.main:app --reload
```

## Tech Stack

- **AI**: OpenAI GPT-4 (function calling)
- **Framework**: FastAPI + Uvicorn
- **Language**: Python 3.11+
- **Container**: Docker + Docker Compose
- **Data**: Mock data (GCP integration planned)

## API Endpoints

Once running, access the API at `http://localhost:8000`:

- `GET /` - Health check
- `POST /api/v1/diagnose` - Diagnose incidents
- `GET /api/v1/tools` - List available tools
- `GET /docs` - Interactive API documentation (Swagger UI)

## Roadmap

- [ ] GCP Cloud Logging & Monitoring integration
- [ ] Cloud Run deployment
- [ ] CI/CD pipeline (GitHub Actions)

## License

MIT
