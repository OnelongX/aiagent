"""Settings · 金融行业特化配置"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Finance AI Assistant"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:8086", "http://localhost:5173"]

    # LLM(OpenAI 协议兼容 · 推荐 livetoken)
    llm_api_base: str = "https://livetoken.top"
    llm_api_key: str = "sk-xxxxx"
    llm_model: str = "claude-sonnet-4-5"

    # 金融机构信息(合规签字栏)
    institution_name: str = "示例银行 / 券商 / 基金公司"
    institution_license: str = "金融许可证编号"
    compliance_officer: str = "示例合规专员"

    # 金融合规(四重保险 · 默认全开)
    pii_redact_enabled: bool = True
    advisor_block_enabled: bool = True       # 投教而非荐股
    aml_threshold_check: bool = True         # 大额 / 可疑交易识别
    suitability_match_required: bool = True  # 适当性匹配强制

    # 监管参考
    large_amount_threshold_rmb: int = 50000      # 5 万元(银行可疑交易 + 大额申报)
    high_frequency_threshold: int = 5            # 单日 ≥5 笔
    cross_border_threshold_usd: int = 10000      # 跨境 1 万美元等值

    # 客服热线
    fraud_hotline: str = "110"            # 反诈
    investor_protect_hotline: str = "12386"  # 证监会投保
    bank_complaint_hotline: str = "12378"    # 银保监投诉

    # 机构类型(影响输出口径)
    institution_type: Literal["bank", "securities", "fund", "insurance"] = "bank"


settings = Settings()
