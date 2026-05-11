"""Settings — loaded from .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Legal Industry AI Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8083", "http://localhost:5173"]

    # LLM(OpenAI 协议兼容 · 推荐 livetoken)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 律所信息(签字栏)
    law_firm_name: str = "示例律师事务所"
    law_firm_license: str = ""

    # 法律数据库(占位 · 接入需付费 API)
    pkulaw_api_key: str = ""
    westlaw_api_key: str = ""

    # Embedding
    embedding_model: str = "BAAI/bge-m3"

    # PII 脱敏
    pii_redact_enabled: bool = True


settings = Settings()
