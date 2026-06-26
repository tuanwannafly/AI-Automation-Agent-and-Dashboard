# AI Automation Agent Backend

FastAPI backend for AI Automation Agent with multi-LLM support, tools, and workflow engine.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Run the server:
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat
- `POST /api/chat` - Create new chat session
- `POST /api/chat/{session_id}` - Send message to session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session
- `GET /api/sessions/{id}/export` - Export session (MD/JSON)

### WebSocket
- `WS /api/ws/{session_id}` - Real-time agent events

### Upload
- `POST /api/upload` - Upload PDF/DOCX file
- `GET /api/uploads` - List uploaded files
- `DELETE /api/uploads/{file_id}` - Delete file

### Workflows
- `GET /api/workflows` - List workflows
- `GET /api/workflows/templates` - List built-in templates
- `GET /api/workflows/templates/{id}` - Get template config
- `POST /api/workflows` - Upload YAML workflow
- `POST /api/workflows/{id}/run` - Run workflow
- `GET /api/runs/{id}` - Get run status

### Health
- `GET /health` - Health check

## LLM Providers

- **Groq** - Fast inference with Llama models
- **OpenAI** - GPT-4o, GPT-3.5
- **Gemini** - Google's Gemini models

## Tools

- `web_search` - Search the web
- `code_executor` - Execute Python code safely
- `calculator` - Mathematical calculations

## Project Structure

```
backend/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py    # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py   # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py      # Chat endpoints
│   │   ├── websocket.py # WebSocket handler
│   │   ├── upload.py    # File upload
│   │   ├── workflows.py # Workflow engine
│   │   └── sessions.py  # Session management
│   └── services/
│       ├── __init__.py
│       ├── llm_provider.py  # LLM providers
│       ├── tools.py         # Available tools
│       └── orchestrator.py  # Agent orchestration
└── workflows/
    └── templates/       # Workflow templates
```