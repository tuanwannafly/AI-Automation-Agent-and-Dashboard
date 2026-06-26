import subprocess
import json
import time
import os
import tempfile

GH = r"C:\Users\ASUS\AppData\Local\Temp\gh\bin\gh.exe"
REPO = "tuanwannafly/AI-Automation-Agent-and-Dashboard"


class APIError(Exception):
    def __init__(self, message, stdout=None, stderr=None, returncode=None):
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def gh_json(method, endpoint, payload=None):
    """Writes payload to a temp JSON file and calls gh api, returns parsed JSON."""
    temp_path = None
    cmd = [GH, "api", "--method", method, endpoint]
    if payload is not None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(payload, f)
            temp_path = f.name
        cmd.extend(["--input", temp_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise APIError(
            f"gh api failed with exit code {e.returncode}",
            stdout=e.stdout,
            stderr=e.stderr,
            returncode=e.returncode,
        ) from e
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        raise

    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)

    if result.stdout.strip():
        return json.loads(result.stdout)
    return {}


def get_all_milestones():
    try:
        return gh_json("GET", f"/repos/{REPO}/milestones?state=all&per_page=100") or []
    except APIError:
        return []


def main():
    # ---- Labels ----
    labels = [
        "phase-0",
        "phase-1",
        "phase-2",
        "phase-3",
        "phase-4",
        "phase-5",
        "phase-6",
        "phase-7",
        "backend",
        "frontend",
        "infrastructure",
        "documentation",
        "security",
        "testing",
    ]

    print("=== Creating Labels ===")
    for label in labels:
        try:
            gh_json("POST", f"/repos/{REPO}/labels", {"name": label, "color": "ffffff"})
            print(f"  Created label: {label}")
        except APIError as e:
            combined = (e.stdout or "") + (e.stderr or "")
            if "already_exists" in combined or "Validation Failed" in combined:
                print(f"  Label already exists: {label}")
            else:
                print(f"  Error creating label {label}: {e}")
                raise

    # ---- Milestones ----
    milestone_defs = [
        {
            "title": "Phase 0: Prerequisites & Setup",
            "description": "Prepare environment, API keys, and repo skeleton before writing code.",
        },
        {
            "title": "Phase 1: Infrastructure Foundation",
            "description": "Docker Compose, FastAPI, WebSocket, LangGraph skeleton, and Groq integration.",
        },
        {
            "title": "Phase 2: Agent Tools Implementation",
            "description": "Tool registry + 4 tools: RAG, Web Search, Code Executor, Summarizer.",
        },
        {
            "title": "Phase 3: LangGraph Orchestration",
            "description": "Planner, Router, Final Answer, Agent Runner streaming, Redis checkpoints.",
        },
        {
            "title": "Phase 4: YAML Workflow Engine",
            "description": "YAML parser/validator, executor, API, templates (CV Analysis).",
        },
        {
            "title": "Phase 5: React Dashboard",
            "description": "Next.js UI: chat, streaming, reasoning chain, file upload, settings.",
        },
        {
            "title": "Phase 6: Integration, Polish & Deploy",
            "description": "E2E integration, file upload backend, multi-LLM, perf, README, demo.",
        },
        {
            "title": "Phase 7: Advanced Features Buffer",
            "description": "OpenAI/Gemini providers, agent memory, workflow gallery, export.",
        },
    ]

    milestone_map = {}  # phase index -> milestone number

    print("\n=== Creating Milestones ===")
    for i, ms_def in enumerate(milestone_defs):
        payload = {
            "title": ms_def["title"],
            "description": ms_def["description"],
            "state": "open",
        }
        try:
            res = gh_json("POST", f"/repos/{REPO}/milestones", payload)
            number = res.get("number")
            if number is None:
                raise ValueError(f"Missing milestone number in response for {ms_def['title']}")
            milestone_map[i] = number
            print(f"  Created milestone #{number}: {ms_def['title']}")
        except APIError as e:
            combined = (e.stdout or "") + (e.stderr or "")
            if "already_exists" in combined or "Validation Failed" in combined:
                existing = get_all_milestones()
                found = next((m for m in existing if m.get("title") == ms_def["title"]), None)
                if found:
                    milestone_map[i] = found["number"]
                    print(f"  Milestone already exists, using #{found['number']}: {ms_def['title']}")
                else:
                    raise RuntimeError(
                        f"Milestone creation failed and could not find existing: {ms_def['title']}"
                    )
            else:
                raise

    # ---- Issues ----
    issue_entries = [
        {"phase": 0, "title": "Setup Accounts & API Keys", "labels": ["phase-0", "infrastructure"], "body": "Prepare .env with all required keys: GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, SERPER_API_KEY, QDRANT_URL, REDIS_URL, SECRET_KEY."},
        {"phase": 0, "title": "Verify Local Environment versions", "labels": ["phase-0", "infrastructure"], "body": "Ensure docker >=24.0, docker compose >=2.24, node >=20, python >=3.11 are installed and working locally."},
        {"phase": 0, "title": "Verify Qdrant from Project 1", "labels": ["phase-0", "infrastructure"], "body": "Confirm P1 Qdrant is running, accessible, and contains at least one collection with data."},
        {"phase": 0, "title": "Initialize Repo & Folder Skeleton", "labels": ["phase-0", "infrastructure", "backend", "frontend"], "body": "Create backend and frontend folder structures, init git repo, create .env.example, and build sandbox Docker image successfully."},
        {"phase": 1, "title": "Docker Compose Setup", "labels": ["phase-1", "infrastructure", "backend"], "body": "Create docker-compose.yml orchestrating backend, frontend, redis, and qdrant services. Ensure hot reload and volume mounts."},
        {"phase": 1, "title": "FastAPI Entrypoint & Config", "labels": ["phase-1", "backend"], "body": "Implement FastAPI app with CORS, health check, and router registration for chat, upload, sessions, workflows, and websocket."},
        {"phase": 1, "title": "Define AgentState TypedDict", "labels": ["phase-1", "backend"], "body": "Create AgentState with fields for user query, plan, tool calls/results, current step, final answer, reasoning chain, session id, and metadata."},
        {"phase": 1, "title": "LangGraph Skeleton & Compile", "labels": ["phase-1", "backend"], "body": "Build StateGraph with planner, router, and final_answer nodes. Add conditional edges and compile graph."},
        {"phase": 1, "title": "WebSocket Endpoint", "labels": ["phase-1", "backend"], "body": "Implement /ws/{session_id} with ConnectionManager, handle PING/PONG, and send/receive events."},
        {"phase": 1, "title": "Chat API Endpoint", "labels": ["phase-1", "backend"], "body": "Create POST /api/chat that returns session_id and ws_url after starting background agent task."},
        {"phase": 1, "title": "Groq LLM Integration", "labels": ["phase-1", "backend"], "body": "Implement streaming (stream_groq) and non-streaming (complete_groq) helpers using AsyncGroq client."},
        {"phase": 2, "title": "Tool Registry Pattern", "labels": ["phase-2", "backend"], "body": "Build ToolRegistry with register decorator, execute dispatch, and get_tool_descriptions for planner prompt injection."},
        {"phase": 2, "title": "RAG Search Tool", "labels": ["phase-2", "backend"], "body": "Implement rag_search tool using Qdrant + sentence-transformers embedder. Return scored results with content, source, and metadata."},
        {"phase": 2, "title": "Web Search Tool (DDG + Serper fallback)", "labels": ["phase-2", "backend"], "body": "Implement web_search using DuckDuckGo with fallback to Serper if rate-limited. Return title, url, snippet."},
        {"phase": 2, "title": "Code Executor (Security Critical)", "labels": ["phase-2", "backend", "security"], "body": "Build Docker sandbox for executing Python code with blocked imports, network disabled, memory/CPU limits, non-root user, and timeout. Backend code_executor tool must run container safely."},
        {"phase": 2, "title": "Summarizer Tool with Map-Reduce", "labels": ["phase-2", "backend"], "body": "Implement summarizer using map-reduce over chunks with LLM calls. Add in-memory cache by content hash."},
        {"phase": 3, "title": "Planner Node", "labels": ["phase-3", "backend"], "body": "Planner node generates JSON step plan based on user query and available tool descriptions using an LLM call."},
        {"phase": 3, "title": "Router Node", "labels": ["phase-3", "backend"], "body": "Router node executes the current step tool, resolves template variables from previous results, and updates state."},
        {"phase": 3, "title": "Final Answer Node", "labels": ["phase-3", "backend"], "body": "Final Answer node compiles tool_results into a coherent user-facing answer using an LLM call."},
        {"phase": 3, "title": "Agent Runner with Event Streaming", "labels": ["phase-3", "backend"], "body": "AgentRunner initializes state, streams LangGraph events, and emits WebSocket events: THINKING, TOOL_CALL, TOOL_RESULT, DONE, ERROR."},
        {"phase": 3, "title": "Redis Checkpoint & Session Persistence", "labels": ["phase-3", "backend"], "body": "Implement SessionManager with save_state, get_state, and delete_session using Redis async client and TTL."},
        {"phase": 4, "title": "YAML Pydantic Schema & Parser", "labels": ["phase-4", "backend"], "body": "Define WorkflowConfig, WorkflowInput, WorkflowStep pydantic models. Parse and validate uploaded YAML. Return 422 on invalid YAML."},
        {"phase": 4, "title": "Workflow Executor with Jinja2", "labels": ["phase-4", "backend"], "body": "Step-by-step executor that evaluates conditions, renders Jinja2 templates, dispatches tools, and collects outputs."},
        {"phase": 4, "title": "Workflow API Endpoints", "labels": ["phase-4", "backend"], "body": "CRUD endpoints: upload workflow (POST), list (GET), run (POST with WS), and get run status (GET)."},
        {"phase": 4, "title": "CV Analysis Pipeline Template", "labels": ["phase-4", "backend", "frontend"], "body": "Create cv_analysis.yaml template: analyze skills -> search market -> generate feedback with Jinja2 interpolation."},
        {"phase": 4, "title": "Auto-Load Built-in Templates", "labels": ["phase-4", "backend"], "body": "On startup or via endpoint, scan workflow/templates/ and expose them via GET /api/workflows/templates."},
        {"phase": 5, "title": "TypeScript Agent Types", "labels": ["phase-5", "frontend"], "body": "Define AgentEventType, AgentEvent, ReasoningStep, LLMProvider, and Message interfaces in frontend."},
        {"phase": 5, "title": "WebSocket Hook (useWebSocket)", "labels": ["phase-5", "frontend"], "body": "Implement useWebSocket hook with auto-reconnect, ping-pong heartbeat, and event streaming."},
        {"phase": 5, "title": "Zustand Agent Store", "labels": ["phase-5", "frontend"], "body": "Create Zustand store for messages, sessionId, streaming text, LLM provider, and workflow selection with event handlers."},
        {"phase": 5, "title": "Main Chat Interface", "labels": ["phase-5", "frontend"], "body": "Build ChatInterface with message list, input area, LLM switcher, status bar, and agent panel sidebar. Integrate WS and REST."},
        {"phase": 5, "title": "ReAct Chain Visualization (AgentPanel)", "labels": ["phase-5", "frontend"], "body": "Implement AgentPanel sidebar to show THINKING, TOOL_CALL, and DONE events with icons and timing."},
        {"phase": 5, "title": "File Upload Component", "labels": ["phase-5", "frontend"], "body": "Build drag & drop file upload for PDF/DOCX using react-dropzone, with upload progress and indexed status."},
        {"phase": 6, "title": "File Upload Backend Endpoint", "labels": ["phase-6", "backend"], "body": "POST /api/upload validates size (<20MB), saves file, extracts text, and indexes into Qdrant."},
        {"phase": 6, "title": "File Processor Service (PDF/DOCX)", "labels": ["phase-6", "backend"], "body": "Service to extract text from PDF (pdfplumber) and DOCX (python-docx) asynchronously."},
        {"phase": 6, "title": "Multi-LLM Provider Factory", "labels": ["phase-6", "backend"], "body": "Factory to route to Groq, OpenAI, or Gemini providers based on request parameter. Implement complete and stream wrappers."},
        {"phase": 6, "title": "Performance Optimization & Retry Logic", "labels": ["phase-6", "backend"], "body": "Add exponential backoff retry decorator for Groq rate limits. Add caching where appropriate."},
        {"phase": 6, "title": "Load Testing & Performance Benchmarks", "labels": ["phase-6", "testing"], "body": "Run locust/k6 to benchmark 50 concurrent sessions. Verify P95 <3s for simple queries and <30s for CV workflow."},
        {"phase": 6, "title": "README & Documentation", "labels": ["phase-6", "documentation"], "body": "Write quick start, architecture, API docs link, and environment setup instructions in README.md."},
        {"phase": 6, "title": "Demo Preparation & End-to-End Polish", "labels": ["phase-6", "documentation", "frontend", "backend"], "body": "Prepare demo scripts, sample CVs/JDs, and verify all demo scenarios run smoothly end-to-end."},
        {"phase": 7, "title": "OpenAI & Gemini Providers", "labels": ["phase-7", "backend"], "body": "Implement complete_openai and complete_gemini with streaming and non-streaming variants."},
        {"phase": 7, "title": "Agent Memory across Sessions", "labels": ["phase-7", "backend"], "body": "Implement AgentMemory to load recent session summaries and save conversation turns for context in future sessions."},
        {"phase": 7, "title": "Workflow Template Gallery UI", "labels": ["phase-7", "frontend"], "body": "Build /workflows page displaying built-in templates as cards with YAML preview and run form."},
        {"phase": 7, "title": "Export Chat + Reasoning", "labels": ["phase-7", "backend"], "body": "Add GET /api/sessions/{id}/export to return session as Markdown or JSON, including reasoning chain and messages."},
    ]

    print("\n=== Creating Issues ===")
    created_issues = []
    for i, issue_def in enumerate(issue_entries):
        phase = issue_def["phase"]
        milestone_number = milestone_map.get(phase)
        if milestone_number is None:
            print(f"  Skipping issue '{issue_def['title']}' - milestone for phase {phase} not found.")
            continue

        payload = {
            "title": issue_def["title"],
            "body": issue_def["body"],
            "labels": issue_def["labels"],
            "milestone": milestone_number,
        }

        try:
            res = gh_json("POST", f"/repos/{REPO}/issues", payload)
            issue_number = res.get("number")
            if issue_number:
                created_issues.append((issue_number, issue_def["title"]))
                print(f"  Created issue #{issue_number}: {issue_def['title']}")
            else:
                print(f"  Warning: No issue number returned for {issue_def['title']}")
        except APIError as e:
            print(f"  Error creating issue '{issue_def['title']}': {e}")

        if i < len(issue_entries) - 1:
            time.sleep(0.5)

    # ---- Summary ----
    print("\n=== Summary ===")
    print(f"Labels processed: {len(labels)}")
    print(f"Milestone map: {milestone_map}")
    print(f"Total issues created: {len(created_issues)}")
    if created_issues:
        print("Created issues:")
        for num, title in created_issues:
            print(f"  #{num}: {title}")


if __name__ == "__main__":
    main()
