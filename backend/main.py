from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import chat, websocket, upload, workflows, sessions

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
app.include_router(workflows.router, prefix=settings.API_PREFIX, tags=["workflows"])
app.include_router(sessions.router, prefix=settings.API_PREFIX, tags=["sessions"])

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