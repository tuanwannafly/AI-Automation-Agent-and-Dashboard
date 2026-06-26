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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")
app.include_router(websocket.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}