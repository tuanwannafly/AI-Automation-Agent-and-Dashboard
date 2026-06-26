from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    openai_api_key: str = ""
    google_api_key: str = ""
    serper_api_key: str = ""
    qdrant_url: str = "http://qdrant:6333"
    redis_url: str = "redis://redis:6379"
    secret_key: str = "dev-secret-key-change-in-production"
    max_code_exec_timeout: int = 30
    max_upload_size_mb: int = 20
    default_llm_provider: str = "groq"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()