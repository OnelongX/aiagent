"""Settings · 教育行业特化配置"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Education AI Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8084", "http://localhost:5173"]

    # LLM(OpenAI 协议兼容 · 推荐 livetoken)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 学校信息(教师签字栏)
    school_name: str = "示例学校"
    teacher_name: str = "示例教师"

    # 学段
    grade_stage: Literal["primary", "junior_high", "senior_high"] = "junior_high"

    # 教育合规(三重保险 · 默认全开)
    pii_redact_enabled: bool = True
    parent_consent_required: bool = True
    double_reduction_mode: bool = True


settings = Settings()
