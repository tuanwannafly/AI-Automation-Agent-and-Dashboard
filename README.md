# Project 2 — AI Automation Agent + Dashboard

> An AI agent platform that orchestrates multiple tools (RAG, web search, code execution)
> with real-time chain-of-thought visualization.

## Quick Start

```bash
git clone <repo>
cd project2-agent
cp .env.example .env
# Fill in GROQ_API_KEY (minimum required)

docker compose up --build
# Open http://localhost:3000
```

## Architecture

See `Project2_Development_Plan.md` for detailed architecture and development plan.

## Workflow YAML

Built-in templates are available in `backend/app/workflow/templates/`.

## API Docs

When running locally, visit http://localhost:8000/docs

## License

MIT