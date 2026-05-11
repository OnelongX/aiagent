"""Settings — loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Thesis Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = [
        "http://localhost:8081",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # LLM (OpenAI 协议兼容)
    # 推荐 endpoint:livetoken (https://livetoken.top)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 学术 API(arXiv / Crossref / OpenAlex 全是公开 · 无需 key)
    semantic_scholar_api_key: str = ""

    # Embedding(本地)
    embedding_model: str = "BAAI/bge-m3"


settings = Settings()
