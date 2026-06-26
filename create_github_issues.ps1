# GitHub Milestones & Issues creation script for Project 2
# Repo: tuanwannafly/AI-Automation-Agent-and-Dashboard
# Run from PowerShell 5.1 or later

$owner = "tuanwannafly"
$repo = "AI-Automation-Agent-and-Dashboard"
$repoPath = "$owner/$repo"

function New-GitHubMilestone($title, $description) {
    $tmp = [System.IO.Path]::GetTempFileName()
    @{ title = $title; description = $description } | ConvertTo-Json -Compress | Set-Content -Path $tmp -Encoding UTF8
    $response = gh api --method POST "/repos/$repoPath/milestones" --input $tmp 2>$null
    Remove-Item $tmp -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create milestone: $title"
        return $null
    }
    $m = $response | ConvertFrom-Json
    return $m.number
}

function New-GitHubIssue($title, $body, $milestone, $labels) {
    $tmp = [System.IO.Path]::GetTempFileName()
    @{ title = $title; body = $body; milestone = $milestone; labels = $labels } | ConvertTo-Json -Compress | Set-Content -Path $tmp -Encoding UTF8
    $response = gh api --method POST "/repos/$repoPath/issues" --input $tmp 2>$null
    Remove-Item $tmp -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create issue: $title"
    }
}

# Create labels
$labels = @("phase-0","phase-1","phase-2","phase-3","phase-4","phase-5","phase-6","phase-7","backend","frontend","infrastructure","documentation","security","testing")
foreach ($lbl in $labels) {
    gh api --method POST "/repos/$repoPath/labels" -f name="$lbl" -f color="000000" 2>$null | Out-Null
}

# Create milestones
Write-Host "Creating milestones..." -ForegroundColor Cyan
$ms = @{}
$ms[0] = New-GitHubMilestone "Phase 0: Prerequisites & Setup" "Prepare environment, API keys, and repo skeleton before writing code."
$ms[1] = New-GitHubMilestone "Phase 1: Infrastructure Foundation" "Docker Compose, FastAPI, WebSocket, LangGraph skeleton, and Groq integration."
$ms[2] = New-GitHubMilestone "Phase 2: Agent Tools Implementation" "Tool registry + 4 tools: RAG, Web Search, Code Executor, Summarizer."
$ms[3] = New-GitHubMilestone "Phase 3: LangGraph Orchestration" "Planner, Router, Final Answer, Agent Runner streaming, Redis checkpoints."
$ms[4] = New-GitHubMilestone "Phase 4: YAML Workflow Engine" "YAML parser/validator, executor, API, templates (CV Analysis)."
$ms[5] = New-GitHubMilestone "Phase 5: React Dashboard" "Next.js UI: chat, streaming, reasoning chain, file upload, settings."
$ms[6] = New-GitHubMilestone "Phase 6: Integration, Polish & Deploy" "E2E integration, file upload backend, multi-LLM, perf, README, demo."
$ms[7] = New-GitHubMilestone "Phase 7: Advanced Features Buffer" "OpenAI/Gemini providers, agent memory, workflow gallery, export."

# Validate milestone numbers
foreach ($k in $ms.Keys | Sort-Object) {
    if ($ms[$k] -eq $null) {
        Write-Error "Milestone for phase $k is null. Aborting."
        exit 1
    }
}

# Define issues
$issuesData = @(
    @{ title="Setup Accounts & API Keys"; phase=0; labels=@("phase-0","infrastructure"); body="Prepare .env with all required keys: GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, SERPER_API_KEY, QDRANT_URL, REDIS_URL, SECRET_KEY."}
    @{ title="Verify Local Environment versions"; phase=0; labels=@("phase-0","infrastructure"); body="Ensure docker >=24.0, docker compose >=2.24, node >=20, python >=3.11 are installed and working locally."}
    @{ title="Verify Qdrant from Project 1"; phase=0; labels=@("phase-0","infrastructure"); body="Confirm P1 Qdrant is running, accessible, and contains at least one collection with data."}
    @{ title="Initialize Repo & Folder Skeleton"; phase=0; labels=@("phase-0","infrastructure","backend","frontend"); body="Create backend and frontend folder structures, init git repo, create .env.example, and build sandbox Docker image successfully."}

    @{ title="Docker Compose Setup"; phase=1; labels=@("phase-1","infrastructure","backend"); body="Create docker-compose.yml orchestrating backend, frontend, redis, and qdrant services. Ensure hot reload and volume mounts."}
    @{ title="FastAPI Entrypoint & Config"; phase=1; labels=@("phase-1","backend"); body="Implement FastAPI app with CORS, health check, and router registration for chat, upload, sessions, workflows, and websocket."}
    @{ title="Define AgentState TypedDict"; phase=1; labels=@("phase-1","backend"); body="Create AgentState with fields for user query, plan, tool calls/results, current step, final answer, reasoning chain, session id, and metadata."}
    @{ title="LangGraph Skeleton & Compile"; phase=1; labels=@("phase-1","backend"); body="Build StateGraph with planner, router, and final_answer nodes. Add conditional edges and compile graph."}
    @{ title="WebSocket Endpoint"; phase=1; labels=@("phase-1","backend"); body="Implement /ws/{session_id} with ConnectionManager, handle PING/PONG, and send/receive events."}
    @{ title="Chat API Endpoint"; phase=1; labels=@("phase-1","backend"); body="Create POST /api/chat that returns session_id and ws_url after starting background agent task."}
    @{ title="Groq LLM Integration"; phase=1; labels=@("phase-1","backend"); body="Implement streaming (stream_groq) and non-streaming (complete_groq) helpers using AsyncGroq client."}

    @{ title="Tool Registry Pattern"; phase=2; labels=@("phase-2","backend"); body="Build ToolRegistry with register decorator, execute dispatch, and get_tool_descriptions for planner prompt injection."}
    @{ title="RAG Search Tool"; phase=2; labels=@("phase-2","backend"); body="Implement rag_search tool using Qdrant + sentence-transformers embedder. Return scored results with content, source, and metadata."}
    @{ title="Web Search Tool (DDG + Serper fallback)"; phase=2; labels=@("phase-2","backend"); body="Implement web_search using DuckDuckGo with fallback to Serper if rate-limited. Return title, url, snippet."}
    @{ title="Code Executor (Security Critical)"; phase=2; labels=@("phase-2","backend","security"); body="Build Docker sandbox for executing Python code with blocked imports, network disabled, memory/CPU limits, non-root user, and timeout. Backend code_executor tool must run container safely."}
    @{ title="Summarizer Tool with Map-Reduce"; phase=2; labels=@("phase-2","backend"); body="Implement summarizer using map-reduce over chunks with LLM calls. Add in-memory cache by content hash."}

    @{ title="Planner Node"; phase=3; labels=@("phase-3","backend"); body="Planner node generates JSON step plan based on user query and available tool descriptions using an LLM call."}
    @{ title="Router Node"; phase=3; labels=@("phase-3","backend"); body="Router node executes the current step tool, resolves Jinja2-like template variables from previous results, and updates state."}
    @{ title="Final Answer Node"; phase=3; labels=@("phase-3","backend"); body="Final Answer node compiles tool_results into a coherent user-facing answer using an LLM call."}
    @{ title="Agent Runner with Event Streaming"; phase=3; labels=@("phase-3","backend"); body="AgentRunner initializes state, streams LangGraph events, and emits WebSocket events: THINKING, TOOL_CALL, TOOL_RESULT, DONE, ERROR."}
    @{ title="Redis Checkpoint & Session Persistence"; phase=3; labels=@("phase-3","backend"); body="Implement SessionManager with save_state, get_state, and delete_session using Redis async client and TTL."}

    @{ title="YAML Pydantic Schema & Parser"; phase=4; labels=@("phase-4","backend"); body="Define WorkflowConfig, WorkflowInput, WorkflowStep pydantic models. Parse and validate uploaded YAML. Return 422 on invalid YAML."}
    @{ title="Workflow Executor with Jinja2"; phase=4; labels=@("phase-4","backend"); body="Step-by-step executor that evaluates conditions, renders Jinja2 templates, dispatches tools, and collects outputs."}
    @{ title="Workflow API Endpoints"; phase=4; labels=@("phase-4","backend"); body="CRUD endpoints: upload workflow (POST), list (GET), run (POST with WS), and get run status (GET)."}
    @{ title="CV Analysis Pipeline Template"; phase=4; labels=@("phase-4","backend","frontend"); body="Create cv_analysis.yaml template: analyze skills -> search market -> generate feedback with Jinja2 interpolation."}
    @{ title="Auto-Load Built-in Templates"; phase=4; labels=@("phase-4","backend"); body="On startup or via endpoint, scan workflow/templates/ and expose them via GET /api/workflows/templates."}

    @{ title="TypeScript Agent Types"; phase=5; labels=@("phase-5","frontend"); body="Define AgentEventType, AgentEvent, ReasoningStep, LLMProvider, and Message interfaces in frontend."}
    @{ title="WebSocket Hook (useWebSocket)"; phase=5; labels=@("phase-5","frontend"); body="Implement useWebSocket hook with auto-reconnect, ping-pong heartbeat, and event streaming."}
    @{ title="Zustand Agent Store"; phase=5; labels=@("phase-5","frontend"); body="Create Zustand store for messages, sessionId, streaming text, LLM provider, and workflow selection with event handlers."}
    @{ title="Main Chat Interface"; phase=5; labels=@("phasesessions"); }", phase=5; labels=@("phase-5","frontend"); body="Build ChatInterface with message list, input area, LLM switcher, status bar, and agent panel sidebar. Integrate WS and REST."}
    @{ title="ReAct Chain Visualization (AgentPanel)"; phase=5; labels=@("phase-5","frontend"); body="Implement AgentPanel sidebar to show THINKING, TOOL_CALL, and DONE events with icons and timing."}
    @{ title="File Upload Component"; phase=5; labels=@("phase-5","frontend"); body="Build drag & drop file upload for PDF/DOCX using react-dropzone, with upload progress and indexed status."}

    @{ title="File Upload Backend Endpoint"; phase=6; labels=@("phase-6","backend"); body="POST /api/upload validates size (<20MB), saves file, extracts text, and indexes into Qdrant."}
    @{ title="File Processor Service (PDF/DOCX)"; phase=6; labels=@("phase-6","backend"); body="Service to extract text from PDF (pdfplumber) and DOCX (python-docx) asynchronously."}
    @{ title="Multi-LLM Provider Factory"; phase=6; labels=@("phase-6","backend"); body="Factory to route to Groq, OpenAI, or Gemini providers based on request parameter. Implement complete and stream wrappers."}
    @{ title="Performance Optimization & Retry Logic"; phase=6; labels=@("phase-6","backend"); body="Add exponential backoff retry decorator for Groq rate limits. Add caching where appropriate."}
    @{ title="Load Testing & Performance Benchmarks"; phase=6; labels=@("phase-6","testing"); body="Run locust/k6 to benchmark 50 concurrent sessions. Verify P95 <3s for simple queries and <30s for CV workflow."}
    @{ title="README & Documentation"; phase=6; labels=@("phase-6","documentation"); body="Write quick start, architecture, API docs link, and environment setup instructions in README.md."}
    @{ title="Demo Preparation & End-to-End Polishrms; details."; phase=6; labels=@("phase-6","documentation","frontend","backend"); body="Prepare demo scripts, sample CVs/JDs, and verify all demo scenarios run smoothly end-to-end."}

    @{ title="OpenAI & Gemini Providers"; phase=7; labels=@("phase-7","backend"); body="Implement complete_openai and complete_gemini with streaming and non-streaming variants."}
    @{ title="Agent Memory across Sessions"; phase=7; labels=@("phase-7","backend"); body="Implement AgentMemory to load recent session summaries and save conversation turns for context in future sessions."}
    @{ title="Workflow Template Gallery UI"; phase=7; labels=@("phase-7","frontend"); body="Build /workflows page displaying built-in templates as cards with YAML preview and run form."}
    @{ title="Export Chat + Reasoning"; phase=7; labels=@("phase-7","backend"); body="Add GET /api/sessions/{id}/export to return session as Markdown or JSON, including reasoning chain and messages."}
)

Write-Host "Creating issues..." -ForegroundColor Cyan
foreach ($issue in $issuesData) {
    $milestoneNum gospel = $ms[$issue.phase]</parameter>
    if ($nullplan -eq new milestoneNum) {
        Write-Error "Milestone for right phase $($issue.phase) not found. Skipping: $($issue.title)"    continue
    }
    New-GitHubIssue -title $issue.title -body $issue.body -milestone $milestoneNum -labels $issue.labels
    Write-Host "Created: $($issue.title)" -ForegroundColor Green
}

Write-Host "All milestones and issues created!" -ForegroundColor Cyan
