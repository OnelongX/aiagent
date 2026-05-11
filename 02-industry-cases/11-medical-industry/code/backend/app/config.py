"""Settings · 医疗行业特化配置"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Medical AI Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8085", "http://localhost:5173"]

    # LLM(OpenAI 协议兼容 · 推荐 livetoken)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 医疗机构信息(医师签字栏)
    hospital_name: str = "示例医院"
    department: str = "示例科室"
    doctor_name: str = "示例医师"
    doctor_license: str = "1100000000000000"

    # 医疗合规(三重保险 · 默认全开)
    pii_redact_enabled: bool = True
    emergency_intercept_enabled: bool = True
    doctor_review_required: bool = True
    drug_db_verify_enabled: bool = True

    # 急救电话
    emergency_phone: str = "120"
    poison_hotline: str = "010-83132345"
    mental_hotline: str = "400-161-9995"


settings = Settings()
