from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://educontrol:password@localhost:5432/educontrol"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "very-long-random-secret-key-256-bits"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    screenshots_path: str = "/var/educontrol/screenshots"
    screenshots_retention_days: int = 30
    backup_path: str = "/var/educontrol/backups"
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_use_tls: bool = True
    max_agents: int = 500
    screenshot_quality: int = 70
    log_level: str = "INFO"

    rate_limit_enabled: bool = False
    docs_enabled: bool = True
    docs_api_key: str = ""
    rate_limit_auth_max: int = 200
    rate_limit_auth_window: int = 60
    rate_limit_api_max: int = 1000
    rate_limit_api_window: int = 60
    rate_limit_monitoring_max: int = 100
    rate_limit_monitoring_window: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
