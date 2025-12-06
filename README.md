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

**Prerequisites:** Python 3.10+, OpenAI API key

> **Get API Key:** Sign up at [platform.openai.com](https://platform.openai.com) → API keys → Create new key

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "USE_MOCK_DATA=true" >> .env

# 3. Run test
python -m src.test_agent
```

## Tech Stack

- **AI**: OpenAI GPT-4 (function calling)
- **Language**: Python 3.10+
- **Data**: Mock data (GCP integration planned)

## Roadmap

- [ ] GCP Cloud Logging & Monitoring integration
- [ ] FastAPI REST API
- [ ] Cloud Run deployment

## License

MIT
