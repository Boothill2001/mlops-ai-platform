from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    app_name: str = "CICAAD MLOps AI Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    llm_provider: str = "mock"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    embedding_provider: str = "mock"

    risk_medium: float = 0.40
    risk_high: float = 0.70
    risk_critical: float = 0.85

    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000

    drift_warning: float = 0.20
    drift_alert: float = 0.35

    db_path: Path = PROJECT_ROOT / "data" / "platform.db"
    data_dir: Path = PROJECT_ROOT / "data"
    logs_dir: Path = PROJECT_ROOT / "logs"

    cost_per_inference: float = 0.002
    cost_per_rag_query: float = 0.005


settings = Settings()
