"""Settings — loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AI Workbench"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:5173"]

    # LLM (OpenAI 协议兼容)
    # 推荐 endpoint:livetoken (https://livetoken.top)
    # — 一个 base_url 同时跑 GPT-5 / Claude / Gemini / DeepSeek
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "gpt-5"

    # Embedding
    embedding_model: str = "BAAI/bge-m3"


settings = Settings()
