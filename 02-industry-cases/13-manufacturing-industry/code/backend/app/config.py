"""Settings · 制造行业特化配置"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Manufacturing AI Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8087", "http://localhost:5173"]

    # LLM(OpenAI 协议兼容 · 推荐 livetoken · 工艺机密建议私有部署 LLM)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 工厂信息(工艺签字栏)
    factory_name: str = "示例工厂"
    workshop: str = "示例车间"
    line_code: str = "L01"
    process_engineer: str = "示例工艺工程师"

    # 制造合规(默认全开)
    pii_redact_enabled: bool = True
    process_boundary_enforced: bool = True     # 工艺参数物理边界硬约束
    qc_double_check_required: bool = True      # 质检 AI 必须 QC 二审
    mes_readonly_mode: bool = True             # MES 默认只读 · 写操作必须人工
    recipe_secret_mask: bool = True            # 配方机密字段脱敏后再进 LLM

    # 车间数据权限(行级隔离)
    user_workshop: str = "*"                   # * 全部 / 否则限定单车间

    # 紧急联系
    safety_hotline: str = "119"                # 火警 / 化学品事故
    eshs_hotline: str = "厂内 EHS 分机 8888"


settings = Settings()
