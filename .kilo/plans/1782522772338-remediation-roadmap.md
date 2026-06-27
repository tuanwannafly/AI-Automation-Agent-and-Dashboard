# Remediation Roadmap: AI Automation Agent

> **Overall state:** 3.5/10 — promising prototype with critical production blockers.  
> **Goal:** production-ready multi-LLM agent platform.

---

## 🔴 Critical (blocks production — fix first)

### 1. Remove RCE in code_executor (`backend/app/services/tools.py:79`)
**Problem:** `exec(code, {"__builtins__": __builtins__}, local_scope)` runs attacker-controlled code with full Python builtins. The AST blocklist is trivially bypassable.
**Fix:** Replace with a real isolated sandbox:
- Option A (recommended): **e2b** sandbox API — one-line integration, Python + filesystem, network isolation.
- Option B: Docker container with `--network=none`, read-only rootfs, seccomp, memory/CPU limits, non-root user.
- Option C: `nsjail` or gVisor process sandbox.
- Never `exec`/`eval` LLM-generated code in-process, even with `RestrictedPython`.

### 2. Remove RCE in workflow condition eval (`backend/app/services/workflow_runner.py:105`)
**Problem:** `eval(condition, {"__builtins__": {}}, {})` where condition is user-uploaded YAML. Escapable even with empty builtins.
**Fix:** Replace with `simpleeval` library (`pip install simpleeval`) — a safe single-expression evaluator. Validate expressions at workflow upload time.

### 3. Add authentication (`backend/main.py`, all routers)
**Problem:** Zero auth. Every endpoint is world-readable/writable.
**Fix:**
- Add `fastapi-users` or a custom `Depends` middleware validating JWT/API-key headers.
- Scope all sessions, uploads, workflows, and RAG queries per authenticated user.
- Add `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE` to config.

### 4. Lock down CORS (`backend/main.py:25-31`)
**Problem:** `allow_origins=["*"]` + `allow_credentials=True` — invalid combo, credential-leak risk.
**Fix:** Restrict to `FRONTEND_ORIGIN` from env, remove `allow_credentials` unless using cookies.

### 5. Persist session/state (`backend/app/services/orchestrator.py`, `rag.py`)
**Problem:** `SessionManager._sessions` and `ChromaVectorStore` are class-level dicts — wiped on restart, unscalable.
**Fix:**
- Sessions, messages, reasoning: **Redis** (`redis-py` + `pydantic` serialization) with TTL.
- Alternately: PostgreSQL via `SQLAlchemy`/`SQLModel` for durable audit trail.
- Uploaded files: move to **S3/MinIO** or a dedicated volume outside the repo.

### 6. Fix broken REST chat endpoint (`backend/app/api/chat.py:41-62`)
**Problem:** `POST /api/chat/{session_id}` creates orchestrator with no-op `event_callback` → never returns assistant content.
**Fix:** Accumulate tokens in an in-memory buffer during `process_message`, return the full response after completion. Or deprecate the REST path in favor of WebSocket-only (simpler).

### 7. Fix workflow create contract mismatch (`frontend/src/lib/api.ts:86` vs `backend/app/api/workflows.py:95`)
**Problem:** Frontend sends JSON body; backend expects multipart YAML upload.
**Fix:** Align contracts — backend should accept JSON body with `WorkflowConfig` Pydantic model; frontend already has the config object ready. Remove multipart requirement for workflow creation.

### 8. Harden file uploads (`backend/app/api/upload.py`)
- Add max file size via FastAPI `File` limits or env config.
- Validate MIME type (not just filename extension) via `python-magic`.
- Write in chunks instead of `await file.read()` (avoid OOM on large files).
- Store uploads outside the source tree (S3/MinIO/`/data/`).
- Sanitize filenames (Path Traversal prevention).

### 9. Stop information leakage
**Problem:** `/health` exposes which providers have keys; errors return raw `str(e)`.
**Fix:** 
- `/health`: remove per-provider key check (just `{"status":"healthy"}`).
- Error responses: return `{"detail":"Internal server error"}` in prod; log real errors server-side.

### 10. Add rate limiting
- `slowapi` decorator on all `/api/*` endpoints (100 req/min per IP, heavier on expensive routes like chat/code_exec).
- Per-user token/cost quotas in Redis.

---

## 🟡 High Value

### 11. Wire real vector RAG
**Problem:** `rag.py` uses in-memory Jaccard keyword overlap despite `chromadb` in requirements.
**Fix:**
- Initialize `chromadb.PersistentClient` from `settings.CHROMA_PERSIST_DIR`.
- Add an embedding function (`sentence-transformers/all-MiniLM-L6-v2` or a provider embedding API).
- Add hybrid search (keyword BM25 + vector) with merged scores.
- Add citation metadata in query results.
- Delete the custom `ChromaVectorStore` fallback class.

### 12. Use native function/tool-calling instead of prompt JSON
**Problem:** `orchestrator.py:129-163` parses LLM output with regex/substrings for tool calls — fragile and unreliable.
**Fix:** Pass `tools` parameter to each provider's chat API (OpenAI, Groq both support the `tools` param with JSON Schema). Parse `tool_calls` from the structured response. Removes the entire regex extraction block.

### 13. Conversation memory (multi-turn)
**Problem:** `orchestrator.py:106` rebuilds `messages=[system, user]` each call — prior turns lost.
**Fix:** Include session message history (up to a context window limit) in each LLM call. Use a sliding window with summarization when the history exceeds the model's token limit.

### 14. Structured logging + observability
**Fix:**
- Replace all `print()` with `structlog` (JSON format, request IDs via middleware).
- Add `opentelemetry-instrumentation-fastapi` for distributed tracing.
- Add `/metrics` endpoint with `prometheus-fastapi-instrumentator`.
- Integrate **Langfuse** or **LangSmith** for LLM call tracing, cost tracking, and eval.

### 15. Real test suite + CI
**Fix:**
- `pytest` + `pytest-asyncio` for backend unit/integration tests.
- Mock LLM providers with `respx` or `httpx.MockTransport`.
- FastAPI `TestClient` for API-level tests.
- Frontend: `vitest` + `@testing-library/react` for components; `playwright` for e2e.
- GitHub Actions workflow: `.github/workflows/ci.yml` (lint → test → build).
- Coverage: minimum 80% gate.

### 16. Containerization
**Fix:**
- `backend/Dockerfile`: multi-stage Python 3.12, `uvicorn` worker, non-root user.
- `frontend/Dockerfile`: multi-stage Next.js build → slim runtime.
- `docker-compose.yml`: api + redis + postgres + chroma (or pgvector) + nginx.
- Drop the `.bat` start scripts.

### 17. Fix Gemini async blocking (`backend/app/services/llm_provider.py:94-105`)
**Problem:** `async def chat` does synchronous `for chunk in response: yield` — blocks event loop.
**Fix:** `loop = asyncio.get_event_loop(); for chunk in await loop.run_in_executor(None, lambda: list(response)): yield chunk.text` or use the async Gemini SDK.

### 18. Fix frontend token rendering O(n) jank (`frontend/src/store/agentStore.ts:96-99`)
**Problem:** Every streaming token triggers `messages.map` to update the last message text.
**Fix:** Track a `streamingBuffer` string in the store; append tokens to it; commit the full buffer to the messages array only on `DONE`.

### 19. Unify workflow engines
**Problem:** `WorkflowRunner` (services/) and `WorkflowExecutor` (api/) duplicate logic.
**Fix:** Delete `WorkflowExecutor` in `workflows.py`, consolidate into `WorkflowRunner` imported from services. Remove the `eval` in `_evaluate_condition` per item #2.

### 20. Gemini conversation history
**Problem:** `GeminiProvider.chat` only sends `messages[-1]`.
**Fix:** Convert the full message list to Gemini's `contents` format (system as `system_instruction`, turns as alternating `user`/`model` parts).

---

## 🟢 Nice to Have

### 21. Developer experience
- Migrate to `pyproject.toml` + `uv.lock` (or `pdm.lock`).
- Add `pre-commit` with ruff, black, mypy, isort.
- Env validation: `pydantic-settings` with `model_config` + fail-fast on missing required keys.

### 22. Repo hygiene
- Purge committed artifacts: `backend.log`, `server.log`, `backend.zip`, `frontend/src.zip`, `backend/app/uploads/*.docx`.
- Expand `.gitignore` to cover `__pycache__/`, `.venv/`, `*.log`, `*.zip`, `backend/app/uploads/` (not just `frontend/node_modules/`).

### 23. Frontend polish
- Persist chat to `localStorage` (or rehydrate from API on reconnect).
- Fix `isConnected` — use `useState` instead of `useRef` (`useWebSocket.ts:150`).
- Add SSE fallback when WebSocket is unavailable.
- Add loading skeletons, error boundaries, toast notifications.

### 24. Security hardening
- `gitleaks` in CI to prevent secret commits.
- `pip-audit` / Dependabot for dependency vulns.
- `bandit` / `semgrep` for SAST scan.
- `helmet` equivalent for Next.js (CSP headers, etc.).

### 25. Documentation
- Architecture diagram (mermaid or excalidraw in `/docs`).
- Production deployment guide.
- Environment variable reference.
- `LICENSE`, `CONTRIBUTING.md`.
- Export OpenAPI schema to `openapi.json`.

---

## Suggested New Features

| Feature | Impact | Notes |
|---|---|---|
| **Native function-calling** | 🟡 | Already covered in item #12 |
| **Agent long-term memory** | 🟡 | Per-user vector memory store + retrieval in system prompt |
| **Human-in-the-loop approval** | 🟡 | Pause workflow/chat before dangerous tool calls, await UI approval |
| **Cost & token dashboards** | 🟢 | Track spend per user/provider; budget alerts |
| **Workflow scheduler (cron)** | 🟢 | `APScheduler` backend; cron expression UI |
| **LLM evals & regression tests** | 🟢 | `promptfoo` or Langfuse eval datasets |
| **Multi-tenancy** | 🟢 | Orgs, projects, RBAC |
| **Model routing & fallback** | 🟢 | Cost/quality-aware router; automatic failover |

---

## Execution Order

1. **Week 1–2:** Items #1–#5 (security: RCEs, auth, CORS, persistence, rate-limit). This makes the system **safe**.
2. **Week 2–3:** Items #6–#10 (fix broken endpoints, upload hardening, info leaks). This makes the system **functional**.
3. **Week 3–5:** Items #11–#16 (real RAG, native tools, conversation memory, logging, tests, containers). This makes it **production-ready**.
4. **Week 5–6:** Items #17–#20 (Gemini fixes, frontend perf, unify engines).
5. **Week 6+:** Items #21–#25 (polish, docs, hygiene) + new features.

## Validation After Each Phase
- **Phase 1:** Manual pen test (can you still RCE? Do unauthenticated requests get 401?)
- **Phase 2:** Full API smoke test (every endpoint returns correct data).
- **Phase 3:** `docker-compose up` + run full test suite + load test 50 concurrent WebSocket sessions.
- **Phase 4:** Frontend manual walkthrough (streaming, workflows, session persistence).
- **Phase 5:** CI green, lint clean, no committed secrets.

---

*Plan generated from full codebase review — 2026-06-27*