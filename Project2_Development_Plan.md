# Project 2 — AI Automation Agent + Dashboard
## Development Plan: Chi Tiết Từng Phase

> **Version:** 1.0 | **Tác giả:** Tuna | **Dựa trên:** BA Analysis v1.0  
> **Tổng thời gian dự kiến:** 7 ngày | **Stack:** FastAPI · LangGraph · React · Docker

---

## MỤC LỤC

1. [Tech Stack & Dependencies](#1-tech-stack--dependencies)
2. [Cấu Trúc Thư Mục Dự Án](#2-cấu-trúc-thư-mục-dự-án)
3. [Phase 0 — Prerequisites & Chuẩn Bị (Trước Day 1)](#phase-0--prerequisites--chuẩn-bị-trước-day-1)
4. [Phase 1 — Infrastructure Foundation (Day 1)](#phase-1--infrastructure-foundation-day-1)
5. [Phase 2 — Agent Tools Implementation (Day 2)](#phase-2--agent-tools-implementation-day-2)
6. [Phase 3 — LangGraph Orchestration & ReAct Loop (Day 3)](#phase-3--langgraph-orchestration--react-loop-day-3)
7. [Phase 4 — YAML Workflow Engine (Day 4)](#phase-4--yaml-workflow-engine-day-4)
8. [Phase 5 — React Dashboard (Day 5)](#phase-5--react-dashboard-day-5)
9. [Phase 6 — Integration, Polish & Deploy (Day 6)](#phase-6--integration-polish--deploy-day-6)
10. [Phase 7 — Advanced Features Buffer (Day 7)](#phase-7--advanced-features-buffer-day-7)
11. [API Contract Reference](#api-contract-reference)
12. [Testing & QA Checklist](#testing--qa-checklist)
13. [Definition of Done](#definition-of-done)
14. [Risk Register](#risk-register)

---

## 1. Tech Stack & Dependencies

### Backend
| Layer | Technology | Version | Lý do chọn |
|---|---|---|---|
| Web Framework | FastAPI | ≥ 0.111 | Async-native, WebSocket built-in |
| Agent Framework | LangGraph | ≥ 0.2 | StateGraph, ReAct loop, streaming-friendly |
| LLM Primary | Groq (Llama 3 70B) | latest | 10–20x faster, streaming-first |
| LLM Fallback | OpenAI GPT-4o / Gemini | latest | Quality fallback |
| Vector DB | Qdrant (reuse P1) | ≥ 1.9 | Đã setup từ Project 1 |
| Session Store | Redis | ≥ 7 | WebSocket session & checkpoint |
| Code Sandbox | Docker SDK (Python) | latest | Isolation cho code_executor |
| Web Search | DuckDuckGo-search + Serper | latest | Free tier + paid fallback |
| YAML Parsing | PyYAML + Pydantic | latest | Validation schema |
| Template Engine | Jinja2 | latest | Variable interpolation trong YAML |
| File Processing | pdfplumber, python-docx | latest | Extract text từ CV |
| Embedding | sentence-transformers | latest | NV-Embed hoặc BAAI |

### Frontend
| Layer | Technology | Version | Lý do chọn |
|---|---|---|---|
| Framework | Next.js 14 (App Router) | 14.x | SSR, built-in routing |
| Language | TypeScript | ≥ 5 | Type safety |
| State Management | Zustand | latest | Nhẹ, đủ cho agent state |
| Styling | Tailwind CSS + shadcn/ui | latest | Rapid UI |
| WebSocket Client | Native WebSocket + custom hook | - | Tự quản lý reconnect |
| File Upload | react-dropzone | latest | Drag & drop |
| Code Highlight | react-syntax-highlighter | latest | Hiển thị code executor output |
| Animation | framer-motion | latest | Streaming token effect |
| HTTP Client | axios | latest | Interceptors, error handling |

### Infrastructure
| Service | Technology | Lý do |
|---|---|---|
| Containerization | Docker + Docker Compose | One-command startup |
| Reverse Proxy | Nginx (production) | HTTPS, WebSocket upgrade |
| Deployment | Railway / Render / VPS | Cloud hosting |
| Monitoring | Prometheus + Grafana (optional) | KPI tracking |

---

## 2. Cấu Trúc Thư Mục Dự Án

```
project2-agent/
├── docker-compose.yml               # Orchestrate tất cả services
├── docker-compose.prod.yml          # Production override
├── .env.example                     # Template env vars
├── .env                             # Local secrets (gitignore)
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                     # DB migrations (nếu cần)
│   ├── app/
│   │   ├── main.py                  # FastAPI app entrypoint
│   │   ├── config.py                # Settings từ env vars
│   │   ├── dependencies.py          # DI: redis, qdrant client
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py              # POST /api/chat
│   │   │   ├── upload.py            # POST /api/upload
│   │   │   ├── sessions.py          # GET /api/sessions/{id}
│   │   │   ├── workflows.py         # CRUD /api/workflows
│   │   │   └── websocket.py         # WS /ws/{session_id}
│   │   │
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── state.py             # AgentState TypedDict
│   │   │   ├── graph.py             # LangGraph StateGraph definition
│   │   │   ├── runner.py            # Graph executor + event emitter
│   │   │   │
│   │   │   ├── nodes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── planner.py       # Planner node
│   │   │   │   ├── router.py        # Tool selector node
│   │   │   │   ├── summarizer.py    # Summarizer node
│   │   │   │   └── final_answer.py  # Final answer node
│   │   │   │
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── registry.py      # ToolRegistry pattern
│   │   │       ├── rag_search.py    # Tool: RAG via Qdrant P1
│   │   │       ├── web_search.py    # Tool: DuckDuckGo + Serper
│   │   │       ├── code_executor.py # Tool: Docker sandbox
│   │   │       └── summarizer.py    # Tool: map-reduce LLM
│   │   │
│   │   ├── workflow/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py            # YAML parser + Pydantic validation
│   │   │   ├── executor.py          # Step-by-step workflow runner
│   │   │   ├── validator.py         # Schema validator
│   │   │   └── templates/           # Built-in YAML templates
│   │   │       ├── cv_analysis.yaml
│   │   │       ├── market_research.yaml
│   │   │       └── data_analysis.yaml
│   │   │
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # LLMProvider abstract class
│   │   │   ├── groq.py              # Groq provider
│   │   │   ├── openai.py            # OpenAI provider
│   │   │   ├── gemini.py            # Gemini provider
│   │   │   └── factory.py           # Provider factory + switcher
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── session.py           # Redis session management
│   │   │   ├── file_processor.py    # PDF/DOCX text extraction
│   │   │   └── qdrant_client.py     # Qdrant connection (reuse P1)
│   │   │
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── chat.py              # Pydantic: ChatRequest, ChatResponse
│   │       ├── workflow.py          # Pydantic: WorkflowConfig, WorkflowRun
│   │       ├── events.py            # Pydantic: AgentEvent types
│   │       └── session.py           # Pydantic: SessionState
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_agent/
│       ├── test_tools/
│       ├── test_workflow/
│       └── test_api/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx             # Main chat page
│   │   │   ├── workflows/
│   │   │   │   └── page.tsx         # Workflow manager
│   │   │   └── settings/
│   │   │       └── page.tsx         # LLM provider settings
│   │   │
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── UserMessage.tsx
│   │   │   │   ├── AgentMessage.tsx      # With streaming token effect
│   │   │   │   ├── ReasoningChain.tsx    # Expandable CoT display
│   │   │   │   └── InputArea.tsx
│   │   │   │
│   │   │   ├── agent/
│   │   │   │   ├── AgentPanel.tsx        # Sidebar: thought process
│   │   │   │   ├── ThoughtProcess.tsx    # Real-time steps
│   │   │   │   ├── ToolCallCard.tsx      # Tool call display
│   │   │   │   ├── ToolResultCard.tsx    # Tool result display
│   │   │   │   └── ExecutionTimeline.tsx # Timeline view
│   │   │   │
│   │   │   ├── upload/
│   │   │   │   └── FileUploadZone.tsx    # Drag & drop
│   │   │   │
│   │   │   ├── workflow/
│   │   │   │   ├── WorkflowSelector.tsx
│   │   │   │   ├── WorkflowStatus.tsx
│   │   │   │   └── YAMLEditor.tsx        # Monaco-lite editor
│   │   │   │
│   │   │   └── ui/
│   │   │       ├── StatusBar.tsx         # WS connection status
│   │   │       ├── LLMSwitcher.tsx       # Provider dropdown
│   │   │       └── TokenCounter.tsx      # Token usage display
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts           # WS connection + auto-reconnect
│   │   │   ├── useAgentSession.ts        # Session state management
│   │   │   ├── useFileUpload.ts          # Upload progress
│   │   │   └── useStreamingText.ts       # Typewriter effect
│   │   │
│   │   ├── store/
│   │   │   ├── agentStore.ts             # Zustand: agent state
│   │   │   ├── sessionStore.ts           # Zustand: session
│   │   │   └── settingsStore.ts          # Zustand: LLM provider, etc.
│   │   │
│   │   ├── types/
│   │   │   ├── agent.ts                  # AgentEvent, AgentState types
│   │   │   ├── workflow.ts               # WorkflowConfig, WorkflowRun
│   │   │   ├── chat.ts                   # Message, Session types
│   │   │   └── api.ts                   # API response types
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                    # Axios client + interceptors
│   │   │   ├── ws.ts                     # WebSocket manager class
│   │   │   └── utils.ts                  # Shared utilities
│   │   │
│   │   └── styles/
│   │       └── globals.css
│   │
│   └── public/
│       └── assets/
│
├── sandbox/
│   ├── Dockerfile.sandbox           # Code executor sandbox image
│   └── executor.py                  # Entrypoint cho sandboxed execution
│
└── nginx/
    ├── nginx.conf                   # WebSocket proxy config
    └── ssl/                         # Certs (production)
```

---

## Phase 0 — Prerequisites & Chuẩn Bị (Trước Day 1)

> **Mục tiêu:** Đảm bảo môi trường sẵn sàng 100% trước khi code. Không setup giữa chừng.

### 0.1 Accounts & API Keys

Cần có sẵn trong `.env`:

```bash
# LLM Providers
GROQ_API_KEY=gsk_...          # groq.com — free tier đủ dùng
OPENAI_API_KEY=sk-...          # fallback (optional)
GOOGLE_API_KEY=AIza...         # Gemini fallback (optional)

# Search
SERPER_API_KEY=...             # serper.dev — $50/month nếu cần
# DuckDuckGo không cần key nhưng rate limit

# Infrastructure
QDRANT_URL=http://qdrant:6333  # Docker internal
QDRANT_API_KEY=                # nếu có auth
REDIS_URL=redis://redis:6379

# App
SECRET_KEY=                    # random 32 bytes
MAX_CODE_EXEC_TIMEOUT=30       # seconds
MAX_UPLOAD_SIZE_MB=20
```

### 0.2 Local Environment Check

```bash
# Verify versions
docker --version        # ≥ 24.0
docker compose version  # ≥ 2.24
node --version          # ≥ 20 (LTS)
python --version        # ≥ 3.11

# Build sandbox image trước
cd sandbox/
docker build -t agent-sandbox:latest -f Dockerfile.sandbox .
docker run --rm agent-sandbox:latest python -c "import numpy; print('OK')"
```

### 0.3 Qdrant từ Project 1

```bash
# Verify P1 Qdrant đang chạy và có data
curl http://localhost:6333/collections
# Expected: collections list từ P1

# Nếu P1 dùng Docker Compose riêng → copy qdrant service vào P2 compose
# hoặc expose port và kết nối cross-network
```

### 0.4 Khởi tạo Repo

```bash
mkdir project2-agent && cd project2-agent
git init
cp /path/to/.env.example .env

# Backend skeleton
mkdir -p backend/app/{api,agent/{nodes,tools},workflow/templates,llm,services,models}
mkdir -p backend/tests/{test_agent,test_tools,test_workflow,test_api}
touch backend/app/__init__.py backend/app/main.py

# Frontend skeleton (Next.js)
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
cd frontend && npx shadcn-ui@latest init

# Sandbox
mkdir sandbox
```

### ✅ Phase 0 Done Khi:
- [ ] `.env` có đủ keys, không còn placeholder
- [ ] `docker build` sandbox image thành công, import numpy/pandas OK
- [ ] Qdrant từ P1 accessible, ít nhất 1 collection có data
- [ ] Repo đã init, folder structure tạo xong
- [ ] `node`, `python`, `docker` versions OK

---

## Phase 1 — Infrastructure Foundation (Day 1)

> **Mục tiêu:** Docker Compose chạy đủ services, FastAPI + WebSocket hoạt động cơ bản, LangGraph skeleton compile được.

### 1.1 Docker Compose Setup (Sáng — 2h)

**File: `docker-compose.yml`**

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app           # Hot reload
      - /var/run/docker.sock:/var/run/docker.sock  # Cho code executor
    depends_on:
      - redis
      - qdrant
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    depends_on:
      - backend
    command: npm run dev

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  redis_data:
  qdrant_data:
```

**Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.2 FastAPI Entrypoint (Sáng — 1h)

**File: `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, upload, sessions, workflows, websocket
from app.config import settings

app = FastAPI(
    title="Project 2 — AI Agent API",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(websocket.router)   # WS endpoint, no prefix

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

**File: `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    openai_api_key: str = ""
    google_api_key: str = ""
    serper_api_key: str = ""
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379"
    secret_key: str
    max_code_exec_timeout: int = 30
    max_upload_size_mb: int = 20
    default_llm_provider: str = "groq"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 1.3 AgentState Definition (Sáng — 30 phút)

**File: `backend/app/agent/state.py`**

```python
from typing import TypedDict, List, Optional, Literal

class AgentState(TypedDict):
    # Input
    user_query: str
    uploaded_files: List[str]
    workflow_config: Optional[dict]

    # Runtime
    plan: List[str]
    tool_calls: List[dict]
    tool_results: List[dict]
    current_step: int
    max_iterations: int         # prevent infinite loop

    # Output
    final_answer: str
    reasoning_chain: List[dict]

    # Meta
    session_id: str
    llm_provider: Literal["groq", "openai", "gemini"]
    tokens_used: int
    execution_time_ms: int
    error: Optional[str]
```

### 1.4 LangGraph Skeleton (Chiều — 2h)

**File: `backend/app/agent/graph.py`**

```python
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.planner import planner_node
from app.agent.nodes.router import router_node
from app.agent.nodes.final_answer import final_answer_node

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("final_answer", final_answer_node)

    # Define flow
    graph.set_entry_point("planner")
    graph.add_edge("planner", "router")

    # Conditional: continue loop or finish
    graph.add_conditional_edges(
        "router",
        lambda state: "final_answer" if _should_finish(state) else "planner",
        {"planner": "planner", "final_answer": "final_answer"}
    )
    graph.add_edge("final_answer", END)

    return graph.compile()

def _should_finish(state: AgentState) -> bool:
    """Finish nếu đã có final answer hoặc vượt max iterations."""
    return (
        bool(state.get("final_answer"))
        or state.get("current_step", 0) >= state.get("max_iterations", 5)
    )

# Singleton compiled graph
agent_graph = build_agent_graph()
```

### 1.5 WebSocket Endpoint (Chiều — 1.5h)

**File: `backend/app/api/websocket.py`**

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.session import SessionManager
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)

    async def send_event(self, session_id: str, event: dict):
        if ws := self.active.get(session_id):
            await ws.send_text(json.dumps(event))

ws_manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            # Keep alive + receive client events (ping, cancel, etc.)
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "PING":
                await ws_manager.send_event(session_id, {"type": "PONG"})
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id)
```

### 1.6 Chat Endpoint cơ bản (Chiều — 1h)

**File: `backend/app/api/chat.py`**

```python
from fastapi import APIRouter, BackgroundTasks
from app.models.chat import ChatRequest, ChatResponse
from app.agent.runner import AgentRunner
from app.api.websocket import ws_manager
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    runner = AgentRunner(session_id=session_id, ws_manager=ws_manager)

    # Run agent in background (non-blocking)
    background_tasks.add_task(runner.run, request)

    return ChatResponse(
        session_id=session_id,
        ws_url=f"ws://localhost:8000/ws/{session_id}",
        status="running"
    )
```

### 1.7 Groq Integration (Chiều — 1h)

**File: `backend/app/llm/groq.py`**

```python
from groq import AsyncGroq
from app.config import settings
from typing import AsyncGenerator

client = AsyncGroq(api_key=settings.groq_api_key)

async def stream_groq(
    messages: list[dict],
    model: str = "llama3-70b-8192",
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """Yield tokens từng token."""
    stream = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
        temperature=temperature,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token

async def complete_groq(messages: list[dict], model: str = "llama3-70b-8192") -> str:
    """Non-streaming complete."""
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=False,
    )
    return response.choices[0].message.content
```

### ✅ Phase 1 Done Khi:
- [ ] `docker compose up` không lỗi, tất cả services healthy
- [ ] `GET /health` trả `{"status": "ok"}`
- [ ] WebSocket connect tới `/ws/test-session` nhận được PONG khi gửi PING
- [ ] `POST /api/chat` trả `session_id` + `ws_url`
- [ ] LangGraph graph compile không lỗi (`agent_graph` import OK)
- [ ] Groq streaming test: `stream_groq` yield tokens ra terminal
- [ ] Unit test: `test_websocket_ping_pong` pass

---

## Phase 2 — Agent Tools Implementation (Day 2)

> **Mục tiêu:** 4 tools hoạt động độc lập, có unit test, integrate vào ToolRegistry.

### 2.1 Tool Registry Pattern (Sáng — 30 phút)

**File: `backend/app/agent/tools/registry.py`**

```python
from typing import Callable, Dict, Any

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, description: str):
        """Decorator để đăng ký tool."""
        def decorator(func: Callable):
            self._tools[name] = func
            self._descriptions[name] = description
            return func
        return decorator

    async def execute(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found. Available: {list(self._tools.keys())}")
        return await self._tools[name](**kwargs)

    def get_tool_descriptions(self) -> str:
        """Trả về descriptions dạng string cho planner prompt."""
        lines = []
        for name, desc in self._descriptions.items():
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)

    @property
    def available_tools(self) -> list[str]:
        return list(self._tools.keys())

tool_registry = ToolRegistry()  # Singleton
```

### 2.2 Tool 1: RAG Search (Sáng — 1h)

**File: `backend/app/agent/tools/rag_search.py`**

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import ScoredPoint
from app.agent.tools.registry import tool_registry
from app.config import settings
from sentence_transformers import SentenceTransformer
from typing import List

# Reuse embedding model từ P1
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
qdrant = AsyncQdrantClient(url=settings.qdrant_url)

@tool_registry.register(
    name="rag_search",
    description="Tìm kiếm tài liệu đã upload vào knowledge base (Qdrant từ Project 1). Dùng khi user hỏi về nội dung file đã index."
)
async def rag_search(
    query: str,
    collection: str = "documents",
    top_k: int = 5,
) -> List[dict]:
    # Embed query
    vector = embedder.encode(query).tolist()

    # Search Qdrant
    results: List[ScoredPoint] = await qdrant.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
    )

    return [
        {
            "content": hit.payload.get("text", ""),
            "source": hit.payload.get("source", "unknown"),
            "score": round(hit.score, 4),
            "metadata": hit.payload,
        }
        for hit in results
    ]
```

**Tests: `backend/tests/test_tools/test_rag_search.py`**
```python
import pytest
from app.agent.tools.rag_search import rag_search

@pytest.mark.asyncio
async def test_rag_search_returns_results():
    results = await rag_search(query="machine learning", top_k=3)
    assert isinstance(results, list)
    if results:  # Có thể empty nếu collection trống
        assert "content" in results[0]
        assert "score" in results[0]

@pytest.mark.asyncio
async def test_rag_search_invalid_collection():
    with pytest.raises(Exception):
        await rag_search(query="test", collection="nonexistent_collection_xyz")
```

### 2.3 Tool 2: Web Search (Sáng — 1.5h)

**File: `backend/app/agent/tools/web_search.py`**

```python
import httpx
from duckduckgo_search import AsyncDDGS
from app.agent.tools.registry import tool_registry
from app.config import settings
from typing import List
import asyncio

@tool_registry.register(
    name="web_search",
    description="Tìm kiếm thông tin trên internet. Dùng khi cần thông tin thời gian thực hoặc kiến thức nằm ngoài tài liệu đã upload."
)
async def web_search(query: str, max_results: int = 5) -> List[dict]:
    """DuckDuckGo với fallback sang Serper nếu rate limit."""
    try:
        return await _ddg_search(query, max_results)
    except Exception as e:
        if settings.serper_api_key:
            return await _serper_search(query, max_results)
        raise e

async def _ddg_search(query: str, max_results: int) -> List[dict]:
    async with AsyncDDGS() as ddgs:
        results = []
        async for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
            if len(results) >= max_results:
                break
        return results

async def _serper_search(query: str, max_results: int) -> List[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            json={"q": query, "num": max_results},
            headers={"X-API-KEY": settings.serper_api_key},
            timeout=10,
        )
        data = response.json()
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
            for item in data.get("organic", [])[:max_results]
        ]
```

### 2.4 Tool 3: Code Executor — CRITICAL (Chiều — 3h)

> ⚠️ **Đây là tool rủi ro cao nhất về security. Phải implement đúng.**

**File: `sandbox/Dockerfile.sandbox`**

```dockerfile
FROM python:3.11-slim

# Whitelist packages only
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.2.1 \
    matplotlib==3.8.3 \
    scikit-learn==1.4.1 \
    pdfplumber==0.11.0

# Non-root user
RUN useradd -m -u 1000 sandbox
USER sandbox
WORKDIR /home/sandbox

# Entrypoint: nhận code qua stdin, output qua stdout
COPY executor.py /home/sandbox/
ENTRYPOINT ["python", "executor.py"]
```

**File: `sandbox/executor.py`**

```python
import sys
import json
import io
import contextlib
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

def run_code(code: str, timeout: int = 30) -> dict:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    local_vars = {}

    try:
        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stderr_capture):
            exec(code, {"__builtins__": __builtins__}, local_vars)
        return {
            "success": True,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "result": str(local_vars.get("result", "")),
        }
    except TimeoutError:
        return {"success": False, "stdout": "", "stderr": "TIMEOUT", "result": ""}
    except Exception as e:
        return {"success": False, "stdout": stdout_capture.getvalue(),
                "stderr": str(e), "result": ""}
    finally:
        signal.alarm(0)

if __name__ == "__main__":
    payload = json.loads(sys.stdin.read())
    result = run_code(payload["code"], payload.get("timeout", 30))
    print(json.dumps(result))
```

**File: `backend/app/agent/tools/code_executor.py`**

```python
import docker
import json
import tempfile
import os
from app.agent.tools.registry import tool_registry
from app.config import settings

docker_client = docker.from_env()

SANDBOX_IMAGE = "agent-sandbox:latest"
BLOCKED_IMPORTS = ["os.system", "subprocess", "socket", "__import__", "eval", "exec"]

@tool_registry.register(
    name="code_executor",
    description="Thực thi Python code trong môi trường sandbox an toàn. Có sẵn: numpy, pandas, matplotlib, scikit-learn. Không có network access."
)
async def code_executor(code: str) -> dict:
    """
    Chạy code trong Docker sandbox.
    Security guarantees:
    - Network disabled
    - Memory limit 256MB
    - CPU limit 0.5
    - Timeout 30s
    - Non-root user
    - Whitelist imports only
    """
    # Pre-check: block dangerous patterns
    for blocked in BLOCKED_IMPORTS:
        if blocked in code:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Blocked: '{blocked}' is not allowed",
                "result": ""
            }

    payload = json.dumps({"code": code, "timeout": settings.max_code_exec_timeout})

    try:
        container = docker_client.containers.run(
            image=SANDBOX_IMAGE,
            command="",
            stdin_open=True,
            stdout=True,
            stderr=True,
            detach=True,
            # Security constraints
            network_mode="none",
            mem_limit="256m",
            nano_cpus=500_000_000,  # 0.5 CPU
            read_only=True,
            tmpfs={"/tmp": "size=50m"},
            security_opt=["no-new-privileges"],
        )

        # Send code via stdin
        socket = container.attach_socket(params={"stdin": 1, "stdout": 1, "stream": 1})
        socket._sock.sendall((payload + "\n").encode())
        socket._sock.close()

        # Wait with timeout
        result = container.wait(timeout=settings.max_code_exec_timeout + 5)
        logs = container.logs(stdout=True, stderr=False).decode()

        container.remove(force=True)
        return json.loads(logs) if logs.strip() else {"success": False, "stdout": "", "stderr": "No output", "result": ""}

    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "result": ""}
```

### 2.5 Tool 4: Summarizer (Chiều — 1h)

**File: `backend/app/agent/tools/summarizer.py`**

```python
from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
from typing import List
import hashlib
import json

# Simple in-memory cache (dùng Redis nếu muốn persist)
_summary_cache: dict = {}

@tool_registry.register(
    name="summarizer",
    description="Tóm tắt văn bản dài (>2000 từ) sử dụng map-reduce. Kết quả được cache theo nội dung."
)
async def summarizer(text: str, max_length: int = 500) -> dict:
    # Cache check
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in _summary_cache:
        return _summary_cache[cache_key]

    # Map: chunk → summarize each chunk
    chunks = _chunk_text(text, chunk_size=3000)
    chunk_summaries = []

    for i, chunk in enumerate(chunks):
        messages = [
            {"role": "system", "content": "You are a precise summarizer. Summarize the given text concisely."},
            {"role": "user", "content": f"Summarize this text segment:\n\n{chunk}"}
        ]
        summary = await complete_groq(messages)
        chunk_summaries.append(summary)

    # Reduce: combine summaries
    if len(chunk_summaries) > 1:
        combined = "\n\n".join(chunk_summaries)
        reduce_messages = [
            {"role": "system", "content": "Combine these summaries into one coherent summary."},
            {"role": "user", "content": combined}
        ]
        final_summary = await complete_groq(reduce_messages)
    else:
        final_summary = chunk_summaries[0] if chunk_summaries else ""

    result = {
        "summary": final_summary,
        "original_length": len(text),
        "summary_length": len(final_summary),
        "chunks_processed": len(chunks),
    }

    _summary_cache[cache_key] = result
    return result

def _chunk_text(text: str, chunk_size: int = 3000) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks
```

### ✅ Phase 2 Done Khi:
- [ ] `tool_registry.available_tools` trả `["rag_search", "web_search", "code_executor", "summarizer"]`
- [ ] `rag_search("python programming")` trả list results (có thể empty)
- [ ] `web_search("latest AI news")` trả ít nhất 3 results
- [ ] `code_executor("result = 1+1")` trả `{"success": true, "result": "2"}`
- [ ] `code_executor("import os; os.system('rm -rf /')")` bị block với error message
- [ ] `summarizer("long text...")` trả dict có `summary` key
- [ ] Unit tests cho cả 4 tools pass
- [ ] Docker sandbox image build OK và network disabled được verify

---

## Phase 3 — LangGraph Orchestration & ReAct Loop (Day 3)

> **Mục tiêu:** Agent có thể tự lên kế hoạch, chọn tool, thực thi, và streaming events ra WebSocket.

### 3.1 Planner Node (Sáng — 1.5h)

**File: `backend/app/agent/nodes/planner.py`**

```python
from app.agent.state import AgentState
from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
import json

PLANNER_SYSTEM_PROMPT = """You are an AI agent planner. Given a user query and the available tools, create a step-by-step plan.

Available tools:
{tool_descriptions}

Rules:
1. Return ONLY a JSON array of steps
2. Each step: {{"step": int, "tool": "tool_name", "reason": "why", "input": {{...}}}}
3. Use "final_answer" as tool if no tools needed
4. Maximum 5 steps
5. Be efficient — don't use tools unnecessarily

Example:
[
  {{"step": 1, "tool": "web_search", "reason": "Need current info", "input": {{"query": "..."}}}},
  {{"step": 2, "tool": "summarizer", "reason": "Summarize results", "input": {{"text": "{{web_search_result}}"}}}}
]"""

async def planner_node(state: AgentState) -> AgentState:
    """Lên kế hoạch dựa trên query và tool descriptions."""
    messages = [
        {
            "role": "system",
            "content": PLANNER_SYSTEM_PROMPT.format(
                tool_descriptions=tool_registry.get_tool_descriptions()
            )
        },
        {
            "role": "user",
            "content": f"User query: {state['user_query']}\n\nPrevious steps completed: {state.get('current_step', 0)}\nTool results so far: {json.dumps(state.get('tool_results', []))}"
        }
    ]

    response = await complete_groq(messages, model="llama3-70b-8192")

    # Parse JSON plan
    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown code block
        import re
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        plan = json.loads(match.group()) if match else []

    return {
        **state,
        "plan": plan,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "THINKING", "content": f"Plan: {plan}", "step": state.get("current_step", 0)}
        ]
    }
```

### 3.2 Router Node (Sáng — 1.5h)

**File: `backend/app/agent/nodes/router.py`**

```python
from app.agent.state import AgentState
from app.agent.tools.registry import tool_registry

async def router_node(state: AgentState) -> AgentState:
    """Thực thi tool hiện tại trong plan."""
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {**state, "final_answer": "No more steps to execute."}

    step = plan[current_step]
    tool_name = step.get("tool", "")
    tool_input = step.get("input", {})

    # Resolve template variables từ previous results
    resolved_input = _resolve_templates(tool_input, state.get("tool_results", []))

    if tool_name == "final_answer":
        # Không cần gọi tool, chuyển sang final answer node
        return {**state, "final_answer": resolved_input.get("content", "")}

    # Execute tool
    try:
        result = await tool_registry.execute(tool_name, **resolved_input)
        success = True
        error = None
    except Exception as e:
        result = str(e)
        success = False
        error = str(e)

    tool_call_record = {
        "step": current_step,
        "tool": tool_name,
        "input": resolved_input,
        "output": result,
        "success": success,
    }

    return {
        **state,
        "tool_calls": state.get("tool_calls", []) + [tool_call_record],
        "tool_results": state.get("tool_results", []) + [result],
        "current_step": current_step + 1,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "TOOL_USE", "tool": tool_name, "result_preview": str(result)[:200]}
        ],
        "error": error,
    }

def _resolve_templates(input_dict: dict, previous_results: list) -> dict:
    """Thay thế {{step_N_result}} bằng actual results."""
    resolved = {}
    for key, value in input_dict.items():
        if isinstance(value, str) and "{{" in value:
            for i, result in enumerate(previous_results):
                value = value.replace(f"{{{{step_{i}_result}}}}", str(result))
        resolved[key] = value
    return resolved
```

### 3.3 Final Answer Node (Sáng — 30 phút)

**File: `backend/app/agent/nodes/final_answer.py`**

```python
from app.agent.state import AgentState
from app.llm.groq import complete_groq
import json

FINAL_ANSWER_PROMPT = """You are an AI assistant. Based on the research and tool results below, provide a comprehensive, helpful answer to the user's question.

Be concise, accurate, and cite sources when available."""

async def final_answer_node(state: AgentState) -> AgentState:
    """Tổng hợp tất cả results thành câu trả lời cuối cùng."""
    if state.get("final_answer"):
        return state  # Already set by router

    context = f"""
User Query: {state['user_query']}

Tool Results:
{json.dumps(state.get('tool_results', []), indent=2, ensure_ascii=False)}
"""

    messages = [
        {"role": "system", "content": FINAL_ANSWER_PROMPT},
        {"role": "user", "content": context}
    ]

    final = await complete_groq(messages)

    return {
        **state,
        "final_answer": final,
        "reasoning_chain": state.get("reasoning_chain", []) + [
            {"type": "DONE", "content": "Final answer generated"}
        ]
    }
```

### 3.4 Agent Runner với Event Streaming (Chiều — 2h)

**File: `backend/app/agent/runner.py`**

```python
from app.agent.state import AgentState
from app.agent.graph import agent_graph
from app.api.websocket import ConnectionManager
from app.models.chat import ChatRequest
import asyncio
import time

class AgentRunner:
    def __init__(self, session_id: str, ws_manager: ConnectionManager):
        self.session_id = session_id
        self.ws_manager = ws_manager

    async def emit(self, event: dict):
        """Gửi event ra WebSocket."""
        await self.ws_manager.send_event(self.session_id, event)

    async def run(self, request: ChatRequest):
        start_time = time.time()

        # Initial state
        initial_state: AgentState = {
            "user_query": request.message,
            "uploaded_files": request.file_ids or [],
            "workflow_config": None,
            "plan": [],
            "tool_calls": [],
            "tool_results": [],
            "current_step": 0,
            "max_iterations": 5,
            "final_answer": "",
            "reasoning_chain": [],
            "session_id": self.session_id,
            "llm_provider": request.llm_provider or "groq",
            "tokens_used": 0,
            "execution_time_ms": 0,
            "error": None,
        }

        await self.emit({"type": "THINKING", "content": "Đang phân tích câu hỏi...", "step": 0})

        try:
            # Stream through LangGraph nodes
            async for event in agent_graph.astream(initial_state):
                # Emit relevant events based on state changes
                for node_name, node_output in event.items():
                    await self._emit_node_events(node_name, node_output)

            # Final state
            final_state = await agent_graph.ainvoke(initial_state)
            elapsed = int((time.time() - start_time) * 1000)

            await self.emit({
                "type": "DONE",
                "final_answer": final_state.get("final_answer", ""),
                "reasoning_chain": final_state.get("reasoning_chain", []),
                "total_tokens": final_state.get("tokens_used", 0),
                "total_time_ms": elapsed,
            })

        except Exception as e:
            await self.emit({
                "type": "ERROR",
                "message": str(e),
                "recoverable": False
            })

    async def _emit_node_events(self, node_name: str, state: dict):
        """Map LangGraph node output → WebSocket events."""
        reasoning_chain = state.get("reasoning_chain", [])
        if reasoning_chain:
            latest = reasoning_chain[-1]
            event_type = latest.get("type", "THINKING")

            if event_type == "THINKING":
                await self.emit({
                    "type": "THINKING",
                    "content": latest.get("content", ""),
                    "step": latest.get("step", 0),
                })
            elif event_type == "TOOL_USE":
                await self.emit({
                    "type": "TOOL_CALL",
                    "tool": latest.get("tool", ""),
                    "input": {},
                })
                await self.emit({
                    "type": "TOOL_RESULT",
                    "tool": latest.get("tool", ""),
                    "output": latest.get("result_preview", ""),
                    "duration_ms": 0,
                })
```

### 3.5 State Persistence với Redis Checkpoint (Chiều — 1h)

```python
# backend/app/services/session.py
import redis.asyncio as aioredis
import json
from app.config import settings

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

class SessionManager:
    @staticmethod
    async def save_state(session_id: str, state: dict, ttl: int = 3600):
        await redis_client.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(state, default=str)
        )

    @staticmethod
    async def get_state(session_id: str) -> dict | None:
        data = await redis_client.get(f"session:{session_id}")
        return json.loads(data) if data else None

    @staticmethod
    async def delete_session(session_id: str):
        await redis_client.delete(f"session:{session_id}")
```

### ✅ Phase 3 Done Khi:
- [ ] End-to-end test: `POST /api/chat` với query đơn giản → WebSocket nhận `THINKING` → `TOOL_CALL` → `TOOL_RESULT` → `DONE`
- [ ] Agent tự chọn đúng tool cho query (web_search cho current events, rag_search cho documents)
- [ ] Error trong tool không làm crash agent — nhận `ERROR` event với `recoverable: true`
- [ ] State được save vào Redis sau mỗi node
- [ ] `GET /api/sessions/{id}` trả lại reasoning chain
- [ ] Max iterations (5) được enforce — không loop vô tận
- [ ] Integration test: agent hoàn thành query trong < 30 giây

---

## Phase 4 — YAML Workflow Engine (Day 4)

> **Mục tiêu:** Upload YAML, parse/validate, run workflow end-to-end, CV Analysis pipeline demo được.

### 4.1 Pydantic Schema cho YAML (Sáng — 1h)

**File: `backend/app/workflow/parser.py`**

```python
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Literal, Any

class WorkflowInput(BaseModel):
    name: str
    type: Literal["file", "text", "number", "boolean"]
    accept: Optional[List[str]] = None   # e.g. [".pdf", ".docx"]
    required: bool = True
    default: Any = None

class WorkflowStep(BaseModel):
    id: str = Field(..., pattern=r'^[a-z_][a-z0-9_]*$')
    tool: Literal["code_executor", "llm_call", "rag_search", "web_search", "summarizer"]
    description: Optional[str] = None
    condition: Optional[str] = None      # Jinja2 expression
    code: Optional[str] = None           # For code_executor
    prompt: Optional[str] = None         # For llm_call
    provider: Optional[str] = "groq"     # For llm_call
    query: Optional[str] = None          # For rag_search
    collection: Optional[str] = "documents"
    top_k: Optional[int] = 5
    input: Optional[dict] = None         # Generic input override
    output_as: str                       # Variable name for result

    @validator('code', always=True)
    def code_required_for_code_executor(cls, v, values):
        if values.get('tool') == 'code_executor' and not v:
            raise ValueError("code is required for code_executor tool")
        return v

class WorkflowConfig(BaseModel):
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    inputs: List[WorkflowInput] = []
    steps: List[WorkflowStep]
    outputs: List[str]        # List of step output_as names to return

def parse_workflow_yaml(yaml_content: str) -> WorkflowConfig:
    import yaml
    data = yaml.safe_load(yaml_content)
    workflow_data = data.get("workflow", data)  # Support both root-level and nested
    return WorkflowConfig(**workflow_data)
```

### 4.2 Workflow Executor (Sáng — 2h)

**File: `backend/app/workflow/executor.py`**

```python
from app.workflow.parser import WorkflowConfig, WorkflowStep
from app.agent.tools.registry import tool_registry
from app.llm.groq import complete_groq
from jinja2 import Environment
import json

jinja_env = Environment()

class WorkflowExecutor:
    def __init__(self, config: WorkflowConfig, inputs: dict):
        self.config = config
        self.inputs = inputs
        self.context: dict = {"inputs": inputs, "steps": {}}  # Jinja2 context
        self.results: dict = {}

    async def run(self, emit_event=None) -> dict:
        """Execute workflow steps in order."""
        for step in self.config.steps:
            # Evaluate condition
            if step.condition:
                should_run = self._evaluate_condition(step.condition)
                if not should_run:
                    self.results[step.output_as] = None
                    continue

            # Emit event
            if emit_event:
                await emit_event({
                    "type": "WORKFLOW_STEP",
                    "step_id": step.id,
                    "description": step.description or step.tool,
                })

            # Execute step
            result = await self._execute_step(step)
            self.results[step.output_as] = result
            self.context["steps"][step.id] = {"output": result}

        # Collect outputs
        return {key: self.results.get(key) for key in self.config.outputs}

    def _evaluate_condition(self, condition: str) -> bool:
        try:
            template = jinja_env.from_string(f"{{{{ {condition} }}}}")
            result = template.render(**self.context)
            return result.strip().lower() not in ("false", "0", "none", "")
        except Exception:
            return True  # Default: run step

    def _render_template(self, text: str) -> str:
        if not text or "{{" not in text:
            return text
        try:
            template = jinja_env.from_string(text)
            return template.render(**self.context)
        except Exception as e:
            return text

    async def _execute_step(self, step: WorkflowStep) -> any:
        if step.tool == "code_executor":
            rendered_code = self._render_template(step.code)
            return await tool_registry.execute("code_executor", code=rendered_code)

        elif step.tool == "llm_call":
            rendered_prompt = self._render_template(step.prompt)
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": rendered_prompt}
            ]
            return await complete_groq(messages)

        elif step.tool == "rag_search":
            rendered_query = self._render_template(step.query or "")
            return await tool_registry.execute(
                "rag_search",
                query=rendered_query,
                collection=step.collection,
                top_k=step.top_k,
            )

        elif step.tool == "web_search":
            rendered_query = self._render_template(step.input.get("query", "") if step.input else "")
            return await tool_registry.execute("web_search", query=rendered_query)

        elif step.tool == "summarizer":
            rendered_text = self._render_template(step.input.get("text", "") if step.input else "")
            return await tool_registry.execute("summarizer", text=rendered_text)

        else:
            raise ValueError(f"Unknown tool: {step.tool}")
```

### 4.3 Workflow API Endpoints (Sáng — 1h)

**File: `backend/app/api/workflows.py`**

```python
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from app.workflow.parser import parse_workflow_yaml, WorkflowConfig
from app.workflow.executor import WorkflowExecutor
from app.api.websocket import ws_manager
import uuid, json
from pathlib import Path

router = APIRouter()

# In-memory store (replace với DB in production)
workflow_store: dict[str, dict] = {}
run_store: dict[str, dict] = {}

@router.post("/workflows")
async def upload_workflow(file: UploadFile = File(...)):
    content = await file.read()
    try:
        config = parse_workflow_yaml(content.decode())
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid YAML: {e}")

    workflow_id = str(uuid.uuid4())
    workflow_store[workflow_id] = {
        "id": workflow_id,
        "name": config.name,
        "config": config.model_dump(),
        "raw_yaml": content.decode(),
    }
    return {"workflow_id": workflow_id, "name": config.name}

@router.get("/workflows")
async def list_workflows():
    return list(workflow_store.values())

@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    inputs: dict,
    background_tasks: BackgroundTasks,
):
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="Workflow not found")

    run_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    run_store[run_id] = {"status": "running", "session_id": session_id, "outputs": {}}

    config = WorkflowConfig(**workflow_store[workflow_id]["config"])
    executor = WorkflowExecutor(config, inputs)

    async def _run():
        try:
            outputs = await executor.run(
                emit_event=lambda e: ws_manager.send_event(session_id, e)
            )
            run_store[run_id]["status"] = "completed"
            run_store[run_id]["outputs"] = outputs
            await ws_manager.send_event(session_id, {"type": "DONE", "outputs": outputs})
        except Exception as e:
            run_store[run_id]["status"] = "failed"
            run_store[run_id]["error"] = str(e)
            await ws_manager.send_event(session_id, {"type": "ERROR", "message": str(e)})

    background_tasks.add_task(_run)

    return {"run_id": run_id, "session_id": session_id,
            "ws_url": f"ws://localhost:8000/ws/{session_id}"}

@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_store[run_id]
```

### 4.4 CV Analysis Pipeline Template (Chiều — 1h)

**File: `backend/app/workflow/templates/cv_analysis.yaml`**

```yaml
workflow:
  name: "CV Analysis Pipeline"
  version: "1.0"
  description: "Tự động phân tích CV ứng viên, so sánh với JD và tạo feedback chi tiết"
  
  inputs:
    - name: cv_text
      type: text
      required: true
    - name: jd_text
      type: text
      required: false
      default: ""
    - name: provider
      type: text
      required: false
      default: "groq"
  
  steps:
    - id: analyze_skills
      tool: llm_call
      description: "Phân tích technical skills, soft skills và kinh nghiệm"
      provider: "{{ inputs.provider }}"
      prompt: |
        Phân tích CV sau và trả về JSON với các field:
        {
          "technical_skills": [...],
          "soft_skills": [...],
          "years_experience": number,
          "education": "...",
          "languages": [...],
          "notable_projects": [...]
        }
        
        CV:
        {{ inputs.cv_text }}
        
        Chỉ trả JSON, không giải thích thêm.
      output_as: skills_analysis

    - id: search_market
      tool: web_search
      description: "Tìm thông tin thị trường lao động liên quan"
      input:
        query: "{{ inputs.cv_text[:100] }} developer job market 2025 Vietnam salary"
      output_as: market_info

    - id: generate_feedback
      tool: llm_call
      description: "Tổng hợp feedback và đưa ra gợi ý cải thiện"
      provider: "{{ inputs.provider }}"
      prompt: |
        Dựa trên phân tích dưới đây, hãy tạo feedback chi tiết bằng tiếng Việt:
        
        **Skills Analysis:**
        {{ steps.analyze_skills.output }}
        
        **Job Description (nếu có):**
        {{ inputs.jd_text | default("Không cung cấp JD") }}
        
        **Thông tin thị trường:**
        {{ steps.search_market.output | string | truncate(1000) }}
        
        Hãy trả về:
        1. **Điểm mạnh** (3-5 điểm)
        2. **Khoảng cách kỹ năng** (nếu có JD)
        3. **Gợi ý cải thiện CV** (cụ thể, actionable)
        4. **Score tổng thể** (0-100) với giải thích
        5. **Mức lương tham khảo** dựa trên thị trường
      output_as: final_feedback
  
  outputs:
    - skills_analysis
    - market_info
    - final_feedback
```

### 4.5 Load Templates tự động (Chiều — 30 phút)

```python
# Thêm vào backend/app/api/workflows.py
from pathlib import Path
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent / "workflow" / "templates"

@router.get("/workflows/templates")
async def list_templates():
    templates = []
    for yaml_file in TEMPLATES_DIR.glob("*.yaml"):
        with open(yaml_file) as f:
            content = yaml.safe_load(f)
            wf = content.get("workflow", content)
            templates.append({
                "id": yaml_file.stem,
                "name": wf.get("name", yaml_file.stem),
                "description": wf.get("description", ""),
                "filename": yaml_file.name,
            })
    return templates

@router.get("/workflows/templates/{template_id}")
async def get_template(template_id: str):
    template_file = TEMPLATES_DIR / f"{template_id}.yaml"
    if not template_file.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return {"content": template_file.read_text()}
```

### ✅ Phase 4 Done Khi:
- [ ] Upload valid YAML → `{"workflow_id": "...", "name": "CV Analysis Pipeline"}`
- [ ] Upload invalid YAML → 422 với clear error message
- [ ] `GET /api/workflows/templates` liệt kê 3 templates
- [ ] `POST /api/workflows/{id}/run` với CV text → nhận WORKFLOW_STEP events + DONE event
- [ ] CV Analysis Pipeline chạy end-to-end trong < 30 giây
- [ ] Conditional step (`condition: "..."`) skip khi condition false
- [ ] Jinja2 variable interpolation giữa steps hoạt động
- [ ] `GET /api/runs/{id}` trả kết quả sau khi completed

---

## Phase 5 — React Dashboard (Day 5)

> **Mục tiêu:** UI đầy đủ: chat + streaming + reasoning chain + file upload + LLM switcher + workflow selector.

### 5.1 TypeScript Types (Sáng — 30 phút)

**File: `frontend/src/types/agent.ts`**

```typescript
export type AgentEventType =
  | "THINKING"
  | "TOOL_CALL"
  | "TOOL_RESULT"
  | "CODE_EXECUTING"
  | "CODE_RESULT"
  | "STREAMING_TOKEN"
  | "WORKFLOW_STEP"
  | "DONE"
  | "ERROR"
  | "PONG";

export interface AgentEvent {
  type: AgentEventType;
  content?: string;
  step?: number;
  tool?: string;
  input?: Record<string, unknown>;
  output?: string;
  duration_ms?: number;
  token?: string;
  step_id?: string;
  description?: string;
  final_answer?: string;
  reasoning_chain?: ReasoningStep[];
  total_tokens?: number;
  total_time_ms?: number;
  outputs?: Record<string, unknown>;
  message?: string;
  recoverable?: boolean;
}

export interface ReasoningStep {
  type: "THINKING" | "TOOL_USE" | "DONE";
  content: string;
  tool?: string;
  result_preview?: string;
  step?: number;
}

export type LLMProvider = "groq" | "openai" | "gemini";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  reasoning?: ReasoningStep[];
  isStreaming?: boolean;
  tokensUsed?: number;
  timeTaken?: number;
}
```

### 5.2 WebSocket Hook (Sáng — 1h)

**File: `frontend/src/hooks/useWebSocket.ts`**

```typescript
import { useEffect, useRef, useCallback, useState } from "react";
import { AgentEvent } from "@/types/agent";

type WSStatus = "connecting" | "connected" | "disconnected" | "error";

export function useWebSocket(sessionId: string | null) {
  const ws = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<WSStatus>("disconnected");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const reconnectTimer = useRef<NodeJS.Timeout>();
  const onEventRef = useRef<((event: AgentEvent) => void) | null>(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/${sessionId}`;
    ws.current = new WebSocket(wsUrl);
    setStatus("connecting");

    ws.current.onopen = () => {
      setStatus("connected");
      // Start ping-pong heartbeat
      const pingInterval = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ type: "PING" }));
        }
      }, 30000);
      ws.current.addEventListener("close", () => clearInterval(pingInterval));
    };

    ws.current.onmessage = (e) => {
      const event: AgentEvent = JSON.parse(e.data);
      if (event.type === "PONG") return;  // Ignore heartbeat
      setEvents((prev) => [...prev, event]);
      onEventRef.current?.(event);
    };

    ws.current.onclose = () => {
      setStatus("disconnected");
      // Auto-reconnect after 3 seconds
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.current.onerror = () => setStatus("error");
  }, [sessionId]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      ws.current?.close();
    };
  }, [connect]);

  const setOnEvent = useCallback((handler: (event: AgentEvent) => void) => {
    onEventRef.current = handler;
  }, []);

  return { status, events, setOnEvent };
}
```

### 5.3 Zustand Store (Sáng — 30 phút)

**File: `frontend/src/store/agentStore.ts`**

```typescript
import { create } from "zustand";
import { Message, LLMProvider, AgentEvent } from "@/types/agent";

interface AgentStore {
  messages: Message[];
  sessionId: string | null;
  currentStreamingText: string;
  isRunning: boolean;
  llmProvider: LLMProvider;
  selectedWorkflowId: string | null;

  addMessage: (message: Message) => void;
  updateLastMessage: (update: Partial<Message>) => void;
  setSessionId: (id: string) => void;
  appendStreamingToken: (token: string) => void;
  finalizeStreaming: () => void;
  setRunning: (running: boolean) => void;
  setLLMProvider: (provider: LLMProvider) => void;
  setWorkflow: (id: string | null) => void;
  handleAgentEvent: (event: AgentEvent) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  messages: [],
  sessionId: null,
  currentStreamingText: "",
  isRunning: false,
  llmProvider: "groq",
  selectedWorkflowId: null,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateLastMessage: (update) =>
    set((state) => {
      const messages = [...state.messages];
      messages[messages.length - 1] = { ...messages[messages.length - 1], ...update };
      return { messages };
    }),

  setSessionId: (id) => set({ sessionId: id }),
  appendStreamingToken: (token) =>
    set((state) => ({ currentStreamingText: state.currentStreamingText + token })),
  finalizeStreaming: () => set({ currentStreamingText: "", isRunning: false }),
  setRunning: (running) => set({ isRunning: running }),
  setLLMProvider: (provider) => set({ llmProvider: provider }),
  setWorkflow: (id) => set({ selectedWorkflowId: id }),

  handleAgentEvent: (event) => {
    const { appendStreamingToken, updateLastMessage, finalizeStreaming } = get();
    switch (event.type) {
      case "STREAMING_TOKEN":
        if (event.token) appendStreamingToken(event.token);
        break;
      case "DONE":
        updateLastMessage({
          content: event.final_answer || get().currentStreamingText,
          reasoning: event.reasoning_chain,
          tokensUsed: event.total_tokens,
          timeTaken: event.total_time_ms,
          isStreaming: false,
        });
        finalizeStreaming();
        break;
      case "ERROR":
        updateLastMessage({ content: `❌ Error: ${event.message}`, isStreaming: false });
        set({ isRunning: false });
        break;
    }
  },
}));
```

### 5.4 Main Chat Interface (Chiều — 2h)

**File: `frontend/src/components/chat/ChatInterface.tsx`**

```tsx
"use client";
import { useState, useRef, useEffect } from "react";
import { useAgentStore } from "@/store/agentStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { MessageList } from "./MessageList";
import { InputArea } from "./InputArea";
import { AgentPanel } from "../agent/AgentPanel";
import { StatusBar } from "../ui/StatusBar";
import { LLMSwitcher } from "../ui/LLMSwitcher";
import api from "@/lib/api";
import { v4 as uuidv4 } from "uuid";

export function ChatInterface() {
  const {
    messages, sessionId, isRunning, llmProvider,
    addMessage, setSessionId, setRunning, handleAgentEvent,
  } = useAgentStore();

  const { status, setOnEvent } = useWebSocket(sessionId);
  const [agentEvents, setAgentEvents] = useState<any[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Register event handler
  useEffect(() => {
    setOnEvent((event) => {
      handleAgentEvent(event);
      setAgentEvents((prev) => [...prev, event]);
    });
  }, [setOnEvent, handleAgentEvent]);

  // Auto-scroll
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text: string, fileIds: string[]) => {
    if (!text.trim() || isRunning) return;

    // Add user message
    addMessage({ id: uuidv4(), role: "user", content: text, timestamp: Date.now() });

    // Add placeholder assistant message
    addMessage({ id: uuidv4(), role: "assistant", content: "", timestamp: Date.now(), isStreaming: true });

    setRunning(true);
    setAgentEvents([]);

    try {
      const response = await api.post("/api/chat", {
        message: text,
        file_ids: fileIds,
        llm_provider: llmProvider,
      });
      setSessionId(response.data.session_id);
    } catch (error) {
      setRunning(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Main chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
          <h1 className="font-semibold text-lg tracking-tight">AI Agent</h1>
          <div className="flex items-center gap-3">
            <LLMSwitcher />
            <StatusBar status={status} />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <MessageList messages={messages} />
          <div ref={scrollRef} />
        </div>

        <InputArea onSend={handleSend} disabled={isRunning} />
      </div>

      {/* Agent panel sidebar */}
      <AgentPanel events={agentEvents} />
    </div>
  );
}
```

### 5.5 ReAct Chain Visualization (Chiều — 1.5h)

**File: `frontend/src/components/agent/AgentPanel.tsx`**

```tsx
"use client";
import { AgentEvent } from "@/types/agent";
import { ToolCallCard } from "./ToolCallCard";
import { useState } from "react";
import { ChevronRight, Brain, Zap } from "lucide-react";

interface Props { events: AgentEvent[] }

export function AgentPanel({ events }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  const relevantEvents = events.filter(
    (e) => ["THINKING", "TOOL_CALL", "TOOL_RESULT", "WORKFLOW_STEP", "DONE"].includes(e.type)
  );

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="w-10 border-l border-gray-800 flex items-center justify-center hover:bg-gray-900 transition-colors"
      >
        <ChevronRight size={16} className="text-gray-400" />
      </button>
    );
  }

  return (
    <div className="w-80 border-l border-gray-800 flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-violet-400" />
          <span className="text-sm font-medium">Thought Process</span>
        </div>
        <button onClick={() => setCollapsed(true)} className="text-gray-500 hover:text-gray-300">
          <ChevronRight size={16} className="rotate-180" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {relevantEvents.length === 0 && (
          <p className="text-xs text-gray-600 text-center mt-8">
            Reasoning steps will appear here during agent execution
          </p>
        )}

        {relevantEvents.map((event, i) => (
          <div key={i}>
            {event.type === "THINKING" && (
              <div className="flex gap-2 p-2 rounded-md bg-gray-900/50">
                <Brain size={14} className="text-violet-400 mt-0.5 shrink-0" />
                <p className="text-xs text-gray-300">{event.content}</p>
              </div>
            )}
            {event.type === "TOOL_CALL" && (
              <ToolCallCard event={event} />
            )}
            {event.type === "DONE" && (
              <div className="flex gap-2 p-2 rounded-md bg-green-900/20 border border-green-800/40">
                <Zap size={14} className="text-green-400 mt-0.5 shrink-0" />
                <div className="text-xs">
                  <p className="text-green-400 font-medium">Completed</p>
                  {event.total_time_ms && (
                    <p className="text-gray-400">{(event.total_time_ms / 1000).toFixed(1)}s · {event.total_tokens} tokens</p>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 5.6 File Upload Component (Chiều — 30 phút)

```tsx
// frontend/src/components/upload/FileUploadZone.tsx
"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import api from "@/lib/api";
import { Upload, FileText, X } from "lucide-react";

interface Props {
  onFileUploaded: (fileId: string, filename: string) => void;
}

export function FileUploadZone({ onFileUploaded }: Props) {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<{id: string; name: string}[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true);
      try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await api.post("/api/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        const fileId = response.data.file_id;
        setUploadedFiles((prev) => [...prev, { id: fileId, name: file.name }]);
        onFileUploaded(fileId, file.name);
      } catch (error) {
        console.error("Upload failed:", error);
      } finally {
        setUploading(false);
      }
    }
  }, [onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
    maxSize: 20 * 1024 * 1024, // 20MB
  });

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-violet-500 bg-violet-500/10" : "border-gray-700 hover:border-gray-600"}`}
      >
        <input {...getInputProps()} />
        <Upload size={20} className="mx-auto text-gray-500 mb-1" />
        <p className="text-xs text-gray-400">
          {uploading ? "Uploading..." : isDragActive ? "Drop files here" : "Drop PDF/DOCX or click to browse"}
        </p>
      </div>

      {uploadedFiles.map((f) => (
        <div key={f.id} className="flex items-center gap-2 p-2 bg-gray-900 rounded text-xs">
          <FileText size={12} className="text-blue-400" />
          <span className="flex-1 truncate text-gray-300">{f.name}</span>
          <span className="text-green-400">✓ Indexed</span>
        </div>
      ))}
    </div>
  );
}
```

### ✅ Phase 5 Done Khi:
- [ ] Chat interface render không lỗi, responsive
- [ ] Gửi message → agent panel hiện THINKING steps trong real-time
- [ ] Token streaming hiển thị typewriter effect
- [ ] File upload drag & drop: upload PDF → toast "File indexed" xuất hiện
- [ ] LLM switcher: switch sang OpenAI → request dùng OpenAI provider
- [ ] WebSocket disconnect → auto-reconnect sau 3 giây, status bar cập nhật
- [ ] Workflow selector hiển thị list, run workflow từ UI
- [ ] Mobile-responsive (tested tại 375px)

---

## Phase 6 — Integration, Polish & Deploy (Day 6)

> **Mục tiêu:** Mọi thứ chạy smooth end-to-end, Docker Compose one-command, README đầy đủ.

### 6.1 File Upload Backend (Sáng — 1h)

**File: `backend/app/api/upload.py`**

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_processor import FileProcessor
from app.services.qdrant_client import index_document
import uuid, os, aiofiles

router = APIRouter()
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate size (20MB)
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")

    # Save to disk
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"

    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    # Extract text
    processor = FileProcessor()
    text = await processor.extract_text(file_path, file.content_type)

    # Index into Qdrant
    await index_document(file_id=file_id, text=text, source=file.filename)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "text_length": len(text),
        "status": "indexed",
    }
```

### 6.2 File Processor Service (Sáng — 1h)

```python
# backend/app/services/file_processor.py
import pdfplumber
from docx import Document
import asyncio

class FileProcessor:
    async def extract_text(self, file_path: str, content_type: str) -> str:
        if "pdf" in content_type:
            return await asyncio.to_thread(self._extract_pdf, file_path)
        elif "docx" in content_type or "wordprocessingml" in content_type:
            return await asyncio.to_thread(self._extract_docx, file_path)
        else:
            # Try reading as plain text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    def _extract_pdf(self, path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()

    def _extract_docx(self, path: str) -> str:
        doc = Document(path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
```

### 6.3 Multi-LLM Provider Factory (Sáng — 1h)

```python
# backend/app/llm/factory.py
from app.config import settings
from typing import Literal

LLMProvider = Literal["groq", "openai", "gemini"]

async def complete(
    messages: list[dict],
    provider: LLMProvider = "groq",
    **kwargs
) -> str:
    if provider == "groq":
        from app.llm.groq import complete_groq
        return await complete_groq(messages, **kwargs)
    elif provider == "openai":
        from app.llm.openai import complete_openai
        return await complete_openai(messages, **kwargs)
    elif provider == "gemini":
        from app.llm.gemini import complete_gemini
        return await complete_gemini(messages, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")

async def stream(provider: LLMProvider = "groq", **kwargs):
    if provider == "groq":
        from app.llm.groq import stream_groq
        return stream_groq(**kwargs)
    # ... other providers
```

### 6.4 Performance Optimization (Sáng — 30 phút)

```python
# Retry + exponential backoff cho Groq
import asyncio
from functools import wraps

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    raise
        return wrapper
    return decorator

# Apply to groq calls
@with_retry(max_retries=3)
async def complete_groq_with_retry(messages, **kwargs):
    return await complete_groq(messages, **kwargs)
```

### 6.5 README.md (Chiều — 1h)

```markdown
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

[Include data flow diagram from BA doc]

## Workflow YAML

[Link to templates + example]

## API Docs

http://localhost:8000/docs
```

### 6.6 Performance & Load Testing (Chiều — 1h)

```bash
# Install k6 or locust
pip install locust

# locustfile.py
from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def run_simple_query(self):
        self.client.post("/api/chat", json={
            "message": "What is machine learning?",
            "llm_provider": "groq"
        })

# Run: locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 5
```

### 6.7 Demo Prep (Chiều — 1h)

**Demo Script (step-by-step):**
1. **Opening:** Mở http://localhost:3000 — clean, dark UI
2. **Demo 1 - Web Search:** Gõ *"Tin tức AI mới nhất tháng này"* → show THINKING + TOOL_CALL web_search + DONE
3. **Demo 2 - Code Executor:** Gõ *"Phân tích dữ liệu này bằng Python: [data]"* → show CODE_EXECUTING + result
4. **Demo 3 - RAG:** Upload CV PDF → "Điểm mạnh của ứng viên này là gì?" → show rag_search tool
5. **Demo 4 - Workflow:** Chọn CV Analysis Pipeline template → upload CV → show WORKFLOW_STEP events → kết quả đẹp
6. **Demo 5 - LLM Switch:** Switch sang Gemini mid-conversation → verify response quality

### ✅ Phase 6 Done Khi:
- [ ] `docker compose up` từ clean state: tất cả services healthy trong < 60 giây
- [ ] Full demo script chạy không lỗi end-to-end
- [ ] File upload 10MB PDF xử lý thành công (< 10 giây)
- [ ] WebSocket ổn định ≥ 10 phút không drop
- [ ] Load test: 50 concurrent sessions không crash
- [ ] `GET /health` tất cả services báo healthy
- [ ] `.env.example` đầy đủ tất cả keys có documentation
- [ ] README.md có quick start, architecture, API docs link

---

## Phase 7 — Advanced Features Buffer (Day 7)

> Chỉ làm nếu Phase 1–6 done sớm. Ưu tiên theo thứ tự.

### Priority 1: OpenAI & Gemini Provider (2h)

```python
# backend/app/llm/openai.py
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def complete_openai(messages: list[dict], model: str = "gpt-4o") -> str:
    response = await client.chat.completions.create(
        messages=messages, model=model, stream=False
    )
    return response.choices[0].message.content
```

### Priority 2: Agent Memory (2h)

```python
# Nhớ context qua nhiều chat sessions
# backend/app/services/memory.py
class AgentMemory:
    """Lưu summary của previous conversations."""

    async def load_context(self, user_id: str, limit: int = 3) -> str:
        """Lấy context từ 3 recent sessions."""
        # Fetch từ Redis hoặc DB
        pass

    async def save_turn(self, user_id: str, query: str, answer: str):
        """Save conversation turn sau khi done."""
        pass
```

### Priority 3: Workflow Template Gallery UI (2h)

```tsx
// Trang workflow gallery với preview cards
// /workflows trang mới
export default function WorkflowsPage() {
  // Hiển thị 3 templates dạng card
  // Click → xem YAML → Run với inputs form
}
```

### Priority 4: Export Chat + Reasoning (1h)

```python
# Export toàn bộ session thành Markdown
@router.get("/sessions/{session_id}/export")
async def export_session(session_id: str, format: str = "markdown"):
    state = await SessionManager.get_state(session_id)
    if format == "markdown":
        return _to_markdown(state)
    elif format == "json":
        return state
```

---

## API Contract Reference

### REST Endpoints

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| POST | `/api/chat` | `{message, file_ids?, llm_provider?}` | `{session_id, ws_url, status}` | Async, returns WS URL |
| POST | `/api/upload` | `multipart/form-data file` | `{file_id, filename, status}` | Max 20MB |
| GET | `/api/sessions/{id}` | - | `{messages, reasoning_chain, ...}` | Full session |
| DELETE | `/api/sessions/{id}` | - | `{deleted: true}` | |
| POST | `/api/workflows` | `multipart YAML file` | `{workflow_id, name}` | |
| GET | `/api/workflows` | - | `[{id, name, description}]` | |
| GET | `/api/workflows/templates` | - | `[{id, name}]` | Built-in templates |
| GET | `/api/workflows/templates/{id}` | - | `{content: "yaml string"}` | |
| POST | `/api/workflows/{id}/run` | `{inputs: {...}}` | `{run_id, session_id, ws_url}` | |
| GET | `/api/runs/{id}` | - | `{status, outputs, error?}` | |
| WS | `/ws/{session_id}` | PING → PONG | Event stream | |
| GET | `/health` | - | `{status: "ok"}` | |

### WebSocket Event Schema

```typescript
// All events sent by server → client
type Event =
  | { type: "THINKING"; content: string; step: number }
  | { type: "TOOL_CALL"; tool: string; input: object }
  | { type: "TOOL_RESULT"; tool: string; output: string; duration_ms: number }
  | { type: "CODE_EXECUTING"; code: string }
  | { type: "CODE_RESULT"; stdout: string; stderr: string; success: boolean }
  | { type: "STREAMING_TOKEN"; token: string }
  | { type: "WORKFLOW_STEP"; step_id: string; description: string }
  | { type: "DONE"; final_answer?: string; reasoning_chain?: object[]; total_tokens: number; total_time_ms: number }
  | { type: "ERROR"; message: string; recoverable: boolean }
  | { type: "PONG" }

// Client → server
type ClientMessage = { type: "PING" } | { type: "CANCEL" }
```

---

## Testing & QA Checklist

### Unit Tests (Mỗi Phase phải pass)

```
backend/tests/
├── test_tools/
│   ├── test_rag_search.py          ✓ Returns results, handles empty
│   ├── test_web_search.py          ✓ DDG success, Serper fallback
│   ├── test_code_executor.py       ✓ Safe code OK, blocked imports rejected
│   └── test_summarizer.py          ✓ Short text, long text chunking
│
├── test_agent/
│   ├── test_planner.py             ✓ Returns valid JSON plan
│   ├── test_router.py              ✓ Executes correct tool, resolves templates
│   └── test_graph.py               ✓ E2E run completes, max iterations enforced
│
├── test_workflow/
│   ├── test_parser.py              ✓ Valid YAML, invalid YAML → 422
│   ├── test_executor.py            ✓ CV pipeline runs, conditional skip works
│   └── test_templates.py           ✓ 3 templates load successfully
│
└── test_api/
    ├── test_chat.py                ✓ POST creates session, returns WS URL
    ├── test_upload.py              ✓ PDF upload, size limit enforced
    ├── test_websocket.py           ✓ PING/PONG, disconnect/reconnect
    └── test_workflows.py           ✓ Upload YAML, list, run
```

### Security Checklist

- [ ] Code executor: `os.system`, `subprocess`, `socket`, `__import__` bị block
- [ ] Code executor container: `docker network inspect` xác nhận network disabled
- [ ] Code executor container: memory limit 256MB được enforce
- [ ] Code executor: timeout 30s được enforce (test với `time.sleep(60)`)
- [ ] Upload: file > 20MB → 413 error
- [ ] Upload: `.exe`, `.sh` files bị reject (chỉ accept PDF, DOCX)
- [ ] CORS: chỉ allow `localhost:3000` trong development
- [ ] No sensitive data (API keys) trong logs

### Performance Checklist

- [ ] Simple query end-to-end: P95 < 3 giây
- [ ] CV Analysis workflow: P95 < 30 giây
- [ ] 50 concurrent WebSocket connections: no crash
- [ ] File indexing 10MB PDF: < 10 giây
- [ ] WebSocket reconnect: < 5 giây sau disconnect

### Demo Readiness

- [ ] CV mẫu tiếng Việt chuẩn bị sẵn (Freshgraduate IT)
- [ ] CV mẫu tiếng Anh chuẩn bị sẵn (Senior Backend Dev)
- [ ] 3 JD mẫu từ thị trường thật (ITviec, LinkedIn)
- [ ] Câu hỏi web_search demo: thị sự, không cần thay đổi
- [ ] Code snippet demo cho code_executor (phân tích CSV đơn giản)
- [ ] Slide backup với screenshots nếu internet chậm

---

## Definition of Done

### Per Phase
Mỗi phase chỉ được coi là done khi:
1. Tất cả checklist items tick ✅
2. Không còn `TODO` hoặc `FIXME` trong code của phase đó
3. Unit tests pass với `pytest -v`
4. Không có unhandled exception trong logs

### Project Complete
- [ ] `docker compose up` cold start: tất cả services healthy
- [ ] Full demo script chạy không có intervention
- [ ] README đủ để người khác setup trong 15 phút
- [ ] `.env.example` documented đầy đủ
- [ ] Security checklist 100%
- [ ] Performance targets đạt theo KPI trong BA doc
- [ ] Code executor isolation verified qua penetration test đơn giản

---

## Risk Register

| # | Rủi ro | Xác suất | Impact | Trigger point | Mitigation |
|---|---|---|---|---|---|
| R1 | Code executor bị exploit | Thấp | Rất cao | Phase 2 | Docker network isolation, whitelist, non-root user |
| R2 | Groq rate limit giữa demo | Trung bình | Cao | Phase 3, 6 | Retry + backoff, OpenAI fallback sẵn |
| R3 | LangGraph breaking API change | Thấp | Trung bình | Phase 3 | Pin version trong requirements.txt |
| R4 | WebSocket drop liên tục | Trung bình | Trung bình | Phase 1, 5 | Auto-reconnect + PING/PONG heartbeat |
| R5 | Qdrant P1 không accessible | Thấp | Cao | Phase 1 | Health check, separate Docker service |
| R6 | YAML injection qua template | Trung bình | Cao | Phase 4 | Jinja2 sandbox mode, input sanitization |
| R7 | Demo internet chậm | Cao | Trung bình | Phase 6 | Cache recent web_search results, slide backup |
| R8 | Memory leak trong long sessions | Thấp | Trung bình | Phase 3 | Session TTL 1h trên Redis, cleanup job |

### Risk Mitigation Actions (Cần làm ngay)

**R1 — Code Executor:**
```bash
# Test isolation ngay sau Phase 2
docker run --rm agent-sandbox:latest python -c "
import socket
try:
    s = socket.socket()
    s.connect(('8.8.8.8', 80))
    print('SECURITY FAIL: network accessible')
except:
    print('OK: network disabled')
"
```

**R6 — YAML Injection:**
```python
# Dùng Jinja2 SandboxedEnvironment thay vì Environment
from jinja2.sandbox import SandboxedEnvironment
jinja_env = SandboxedEnvironment()  # Blocks dangerous expressions
```

---

*Document này là nguồn sự thật duy nhất cho quá trình phát triển Project 2.*  
*Cập nhật document này khi có thay đổi kiến trúc hoặc requirements.*

**Tổng estimated time:**
- Phase 0: 2–3h (prep)
- Phase 1–6: 6 ngày × 6–8h = ~42h coding
- Phase 7: 1 ngày buffer nếu cần

*Version: 1.0 | Dựa trên BA Analysis v1.0*
