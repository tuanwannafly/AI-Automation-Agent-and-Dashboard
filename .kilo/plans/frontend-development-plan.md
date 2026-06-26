# Frontend Development Plan - AI Automation Agent Dashboard

## Tổng quan

Frontend được xây dựng bằng **Next.js 14 + TypeScript + Tailwind CSS**, tích hợp với Backend API đã hoàn thành qua 8 phases.

## API Endpoints Available

### REST APIs
| Method | Endpoint | Description | Phase |
|--------|----------|-------------|-------|
| POST | `/api/chat` | Start new chat session | BE Phase 3 |
| GET | `/api/sessions/{id}` | Get session state | BE Phase 3 |
| DELETE | `/api/sessions/{id}` | Delete session | BE Phase 3 |
| POST | `/api/upload` | Upload file (PDF/DOCX) | BE Phase 6 |
| POST | `/api/workflows` | Upload YAML workflow | BE Phase 4 |
| GET | `/api/workflows` | List workflows | BE Phase 4 |
| GET | `/api/workflows/templates` | List built-in templates | BE Phase 4 |
| GET | `/api/workflows/templates/{id}` | Get template content | BE Phase 4 |
| POST | `/api/workflows/{id}/run` | Run workflow | BE Phase 4 |
| GET | `/api/runs/{id}` | Get run status | BE Phase 4 |
| GET | `/api/sessions/{id}/export` | Export session (MD/JSON) | BE Phase 7 |
| POST | `/api/sessions/{id}/memory` | Save session memory | BE Phase 7 |
| GET | `/api/sessions/{id}/context` | Get session context | BE Phase 7 |
| GET | `/health` | Health check | BE Phase 1 |

### WebSocket
| Endpoint | Description | Phase |
|----------|-------------|-------|
| `/ws/{session_id}` | Real-time agent events | BE Phase 3 |

**Event Types:** `THINKING`, `TOOL_CALL`, `TOOL_RESULT`, `STREAMING_TOKEN`, `WORKFLOW_STEP`, `DONE`, `ERROR`, `PONG`

---

## Frontend Phases

### Phase FE-0: Foundation & Setup
**Mục tiêu:** Setup Next.js project với đầy đủ dependencies và cấu hình cơ bản.

**Tasks:**
1. Khởi tạo Next.js 14 project với App Router
2. Cài đặt dependencies: TypeScript, Tailwind CSS, Zustand, axios, uuid, lucide-react, react-dropzone
3. Cấu hình tsconfig.json, next.config.js, tailwind.config.js
4. Tạo folder structure: `src/types`, `src/hooks`, `src/store`, `src/components`, `src/lib`, `src/app`
5. Setup globals.css với dark theme
6. Tạo API client wrapper với axios interceptors

**Deliverables:**
- ✅ `package.json` với đầy đủ dependencies
- ✅ `tsconfig.json`, `next.config.js`, `tailwind.config.js`
- ✅ Folder structure hoàn chỉnh
- ✅ `src/lib/api.ts` - API client

---

### Phase FE-1: Type Definitions & Store
**Mục tiêu:** Định nghĩa TypeScript types và Zustand store cho toàn bộ application.

**Tasks:**
1. Định nghĩa types cho AgentEvent (tất cả event types từ WebSocket)
2. Định nghĩa types cho Message, ReasoningStep, SessionState
3. Định nghĩa types cho Workflow (WorkflowConfig, WorkflowStep, WorkflowRun)
4. Định nghĩa types cho LLMProvider, FileUpload
5. Tạo Zustand store cho agent state (messages, sessionId, streaming, isRunning)
6. Tạo Zustand store cho settings (llmProvider, workflow selection)
7. Tạo Zustand store cho file uploads

**Deliverables:**
- ✅ `src/types/agent.ts` - AgentEvent, Message, ReasoningStep
- ✅ `src/types/workflow.ts` - Workflow types
- ✅ `src/types/api.ts` - API response types
- ✅ `src/store/agentStore.ts` - Agent state management
- ✅ `src/store/settingsStore.ts` - Settings management

---

### Phase FE-2: WebSocket Integration
**Mục tiêu:** Implement WebSocket hook với auto-reconnect và event handling.

**Tasks:**
1. Tạo `useWebSocket` hook với connection management
2. Implement auto-reconnect với exponential backoff
3. Implement ping-pong heartbeat (30s interval)
4. Parse và dispatch WebSocket events
5. Handle connection states: connecting, connected, disconnected, error
6. Tạo event queue cho offline events

**Deliverables:**
- ✅ `src/hooks/useWebSocket.ts` - WebSocket hook
- ✅ Connection status indicator component
- ✅ Event types handling

---

### Phase FE-3: Chat Interface Core
**Mục tiêu:** Implement chat interface cơ bản với message list và input.

**Tasks:**
1. Tạo `ChatInterface` component layout
2. Implement `MessageList` component với user/assistant messages
3. Implement `InputArea` component với textarea và send button
4. Handle Enter key to send, Shift+Enter for new line
5. Implement streaming text display (typewriter effect)
6. Integrate với API `/api/chat` endpoint
7. Connect WebSocket events để hiển thị real-time updates

**Deliverables:**
- ✅ `src/components/chat/ChatInterface.tsx`
- ✅ `src/components/chat/MessageList.tsx`
- ✅ `src/components/chat/InputArea.tsx`
- ✅ `src/components/chat/StreamingText.tsx`

---

### Phase FE-4: Agent Reasoning Visualization
**Mục tiêu:** Hiển thị chain-of-thought và tool execution của agent.

**Tasks:**
1. Tạo `AgentPanel` sidebar component
2. Implement `ThoughtProcess` component cho THINKING events
3. Implement `ToolCallCard` component cho TOOL_CALL events
4. Implement `ToolResultCard` component cho TOOL_RESULT events
5. Implement `ExecutionTimeline` component cho workflow steps
6. Add collapsible sidebar với animation
7. Highlight events theo type (thinking=violet, tool=blue, result=green)

**Deliverables:**
- ✅ `src/components/agent/AgentPanel.tsx`
- ✅ `src/components/agent/ThoughtProcess.tsx`
- ✅ `src/components/agent/ToolCallCard.tsx`
- ✅ `src/components/agent/ToolResultCard.tsx`
- ✅ `src/components/agent/ExecutionTimeline.tsx`

---

### Phase FE-5: File Upload Component
**Mục tiêu:** Implement drag & drop file upload cho PDF/DOCX.

**Tasks:**
1. Tạo `FileUploadZone` component với react-dropzone
2. Handle drag & drop events
3. Validate file type (PDF, DOCX only) và size (max 20MB)
4. Upload progress indicator
5. Display uploaded files list với status
6. Integrate với `/api/upload` endpoint
7. Show indexed status sau khi upload hoàn tất

**Deliverables:**
- ✅ `src/components/upload/FileUploadZone.tsx`
- ✅ `src/components/upload/UploadedFileList.tsx`
- ✅ `src/hooks/useFileUpload.ts`

---

### Phase FE-6: LLM Provider Switcher
**Mục tiêu:** Cho phép user switch giữa Groq, OpenAI, Gemini.

**Tasks:**
1. Tạo `LLMSwitcher` dropdown component
2. Lưu provider selection vào settings store
3. Display provider status/availability
4. Send provider selection trong `/api/chat` request
5. Hiển thị current provider trong UI header

**Deliverables:**
- ✅ `src/components/ui/LLMSwitcher.tsx`
- ✅ Provider selection persistence
- ✅ Integration với chat API

---

### Phase FE-7: Workflow Management UI
**Mục tiêu:** UI để xem templates, upload workflows, và run workflows.

**Tasks:**
1. Tạo `/workflows` page với template gallery
2. Implement `WorkflowSelector` component
3. Implement `WorkflowStatus` component cho running workflows
4. Tạo `YAMLEditor` component (Monaco-lite) để xem/edit YAML
5. Fetch templates từ `/api/workflows/templates`
6. Upload workflow từ template
7. Run workflow với inputs form
8. Display workflow execution events qua WebSocket

**Deliverables:**
- ✅ `src/app/workflows/page.tsx` - Template gallery
- ✅ `src/components/workflow/WorkflowSelector.tsx`
- ✅ `src/components/workflow/WorkflowStatus.tsx`
- ✅ `src/components/workflow/YAMLEditor.tsx`
- ✅ `src/components/workflow/WorkflowInputsForm.tsx`

---

### Phase FE-8: Session Management
**Mục tiêu:** Quản lý sessions, export, và context history.

**Tasks:**
1. Tạo `/sessions` page để xem session history
2. Implement session list với search/filter
3. View session detail với full reasoning chain
4. Export session as Markdown/JSON
5. Load context từ previous sessions
6. Delete session functionality

**Deliverables:**
- ✅ `src/app/sessions/page.tsx` - Session list
- ✅ `src/app/sessions/[id]/page.tsx` - Session detail
- ✅ `src/components/session/SessionList.tsx`
- ✅ `src/components/session/ExportButton.tsx`

---

### Phase FE-9: Settings Page
**Mục tiêu:** Settings page để cấu hình API keys và preferences.

**Tasks:**
1. Tạo `/settings` page
2. Form để nhập API keys (Groq, OpenAI, Gemini)
3. Toggle dark/light mode (optional)
4. Configure max iterations, timeout settings
5. Test connection button cho mỗi LLM provider
6. Save settings to localStorage

**Deliverables:**
- ✅ `src/app/settings/page.tsx`
- ✅ `src/components/settings/APIKeyForm.tsx`
- ✅ `src/components/settings/LLMTestConnection.tsx`

---

### Phase FE-10: Polish & Integration
**Mục tiêu:** Hoàn thiện UI, responsive, error handling, và demo prep.

**Tasks:**
1. Responsive design cho mobile (375px breakpoint)
2. Error handling và toast notifications
3. Loading states cho tất cả async operations
4. Empty states cho messages, workflows, sessions
5. Keyboard shortcuts (Ctrl+Enter to send, Esc to cancel)
6. Performance optimization (memo, lazy loading)
7. Demo script preparation
8. Final testing end-to-end

**Deliverables:**
- ✅ Responsive design across all breakpoints
- ✅ Error boundaries và fallback UIs
- ✅ Toast notifications system
- ✅ Demo-ready application

---

## Component Tree

```
app/
├── layout.tsx
├── page.tsx (Home -> redirects to /chat)
├── chat/
│   └── page.tsx (ChatInterface)
├── workflows/
│   └── page.tsx (Workflow Gallery)
├── sessions/
│   ├── page.tsx (Session List)
│   └── [id]/
│       └── page.tsx (Session Detail)
└── settings/
    └── page.tsx (Settings)

components/
├── chat/
│   ├── ChatInterface.tsx
│   ├── MessageList.tsx
│   ├── UserMessage.tsx
│   ├── AgentMessage.tsx
│   ├── ReasoningChain.tsx
│   └── InputArea.tsx
├── agent/
│   ├── AgentPanel.tsx
│   ├── ThoughtProcess.tsx
│   ├── ToolCallCard.tsx
│   ├── ToolResultCard.tsx
│   └── ExecutionTimeline.tsx
├── upload/
│   ├── FileUploadZone.tsx
│   └── UploadedFileList.tsx
├── workflow/
│   ├── WorkflowSelector.tsx
│   ├── WorkflowStatus.tsx
│   ├── YAMLEditor.tsx
│   └── WorkflowInputsForm.tsx
├── session/
│   ├── SessionList.tsx
│   ├── SessionDetail.tsx
│   └── ExportButton.tsx
├── settings/
│   ├── APIKeyForm.tsx
│   └── LLMTestConnection.tsx
└── ui/
    ├── StatusBar.tsx
    ├── LLMSwitcher.tsx
    ├── TokenCounter.tsx
    └── Toast.tsx
```

---

## Mapping Backend APIs → Frontend Components

| Backend Endpoint | Frontend Components | Phase |
|-----------------|---------------------|-------|
| POST `/api/chat` | ChatInterface, InputArea | FE-3 |
| WS `/ws/{session_id}` | useWebSocket, AgentPanel | FE-2, FE-4 |
| POST `/api/upload` | FileUploadZone | FE-5 |
| GET `/api/workflows/templates` | Workflow Gallery | FE-7 |
| POST `/api/workflows` | Workflow Gallery | FE-7 |
| POST `/api/workflows/{id}/run` | WorkflowInputsForm | FE-7 |
| GET `/api/sessions/{id}` | Session Detail | FE-8 |
| GET `/api/sessions/{id}/export` | ExportButton | FE-8 |
| POST `/api/sessions/{id}/memory` | Session Context | FE-8 |

---

## Testing Checklist

### Unit Tests
- [ ] `useWebSocket` hook - connect, disconnect, reconnect
- [ ] `agentStore` - addMessage, handleAgentEvent
- [ ] `FileUploadZone` - file validation, upload
- [ ] API client - interceptors, error handling

### Integration Tests
- [ ] Chat flow: send message → receive THINKING → TOOL_CALL → TOOL_RESULT → DONE
- [ ] File upload: select file → upload → indexed status
- [ ] Workflow: select template → run → view events
- [ ] Session export: view session → export Markdown

### E2E Demo Scenarios
1. Web search query → show tool execution
2. Code executor query → run Python code
3. CV upload → RAG search → analysis
4. Workflow: CV Analysis Pipeline → full execution

---

## Timeline & Phases Summary

| Phase | Name | Estimated Tasks | Priority |
|-------|------|-----------------|----------|
| FE-0 | Foundation & Setup | 6 tasks | High |
| FE-1 | Types & Store | 7 tasks | High |
| FE-2 | WebSocket | 6 tasks | High |
| FE-3 | Chat Core | 7 tasks | High |
| FE-4 | Reasoning UI | 7 tasks | High |
| FE-5 | File Upload | 7 tasks | High |
| FE-6 | LLM Switcher | 5 tasks | Medium |
| FE-7 | Workflow UI | 8 tasks | High |
| FE-8 | Sessions | 6 tasks | Medium |
| FE-9 | Settings | 6 tasks | Low |
| FE-10 | Polish | 8 tasks | High |

**Total:** ~75 tasks across 11 phases

---

## Next Steps

1. ✅ Save this plan
2. ✅ Create GitHub milestones for FE phases
3. ✅ Create GitHub issues for each task
4. ✅ Start implementation from FE-0