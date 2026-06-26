# Project 2 — AI Automation Agent + Dashboard

> An AI agent platform that orchestrates multiple tools (RAG, web search, code execution)
> with real-time chain-of-thought visualization.

## Quick Start

```bash
git clone https://github.com/tuanwannafly/AI-Automation-Agent-and-Dashboard.git
cd AI-Automation-Agent-and-Dashboard
git clone <repo>
cd project2-agent
cp .env.example .env
# Fill in GROQ_API_KEY (minimum required)

docker compose up --build
# Open http://localhost:3000
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│   Tools     │
│  (Next.js)  │ WS  │  (FastAPI)   │ RPC │  Registry   │
└─────────────┘     └──────────────┘     └─────────────┘
                          │                    │
                          ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  LangGraph   │     │  Qdrant     │
                    │  (ReAct)     │     │  (Vector)   │
                    └──────────────┘     └─────────────┘
```

### Components

- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Zustand
- **Backend**: FastAPI + LangGraph + Groq/OpenAI/Gemini
- **Tools**: RAG (Qdrant), Web Search, Code Executor (Docker sandbox), Summarizer
- **Workflow Engine**: YAML-based pipeline execution

## Features

- **Multi-LLM Support**: Groq (Llama 3), OpenAI (GPT-4o), Gemini
- **Tool Use**: Agent can use RAG, web search, code execution, summarization
- **Chain of Thought**: Real-time visualization of agent reasoning
- **Workflow Automation**: YAML-defined pipelines for complex tasks
- **Sandboxed Code Execution**: Secure Python execution in Docker

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Start new chat session |
| POST | `/api/upload` | Upload file (PDF/DOCX) |
| GET | `/api/sessions/{id}` | Get session state |
| POST | `/api/workflows` | Upload YAML workflow |
| GET | `/api/workflows/templates` | List built-in templates |
| POST | `/api/workflows/{id}/run` | Run workflow |
| WS | `/ws/{session_id}` | WebSocket event stream |

Full API docs: http://localhost:8000/docs

## Workflow Templates

Built-in templates:
- `cv_analysis.yaml` - CV analysis with skills extraction and feedback
- `market_research.yaml` - Web search + summarization pipeline
- `data_analysis.yaml` - Python code execution for data analysis

Example usage:
```bash
# List templates
curl http://localhost:8000/api/workflows/templates

# Get template content
curl http://localhost:8000/api/workflows/templates/cv_analysis

# Run workflow
curl -X POST http://localhost:8000/api/workflows/{id}/run \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"cv_text": "...", "jd_text": "..."}}'
```

## Environment Variables

```bash
# LLM Providers (at least one required)
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Search (optional)
SERPER_API_KEY=...

# Infrastructure
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
```

## Development

```bash
# Backend only
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend only
cd frontend
npm install
npm run dev

# Run tests
pytest backend/tests
```
See `Project2_Development_Plan.md` for detailed architecture and development plan.

## Workflow YAML

Built-in templates are available in `backend/app/workflow/templates/`.

## API Docs

When running locally, visit http://localhost:8000/docs

## License

MIT