import sys
import io

# Ensure stdout/stderr use UTF-8 on Windows so emoji and other non-cp1252
# characters emitted by LLM streams don't crash with UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat, websocket, upload, workflows, sessions

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix=settings.API_PREFIX, tags=["chat"])
app.include_router(websocket.router, prefix=settings.API_PREFIX, tags=["websocket"])
app.include_router(upload.router, prefix=settings.API_PREFIX, tags=["upload"])
app.include_router(workflows.router, prefix=f"{settings.API_PREFIX}/workflows", tags=["workflows"])
app.include_router(sessions.router, prefix=f"{settings.API_PREFIX}/sessions", tags=["sessions"])

@app.get("/health")
async def health():
    providers_status = {}
    for provider in ["groq", "openai", "gemini"]:
        key = getattr(settings, f"{provider.upper()}_API_KEY", "")
        providers_status[provider] = bool(key)
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime": "N/A",
        "llmProviders": providers_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)