from functools import lru_cache
from typing import List
import os
from pydantic import Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Fallback nếu pydantic-settings chưa được cài
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = None


class Settings(BaseSettings):
    """Quản lý biến môi trường tập trung cho FastAPI Backend."""

    # Server Settings
    app_name: str = "Weather Forecast Bias Correction MLOps"
    app_env: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"

    # Security & Auth
    api_key: str = "weather-mlops-dev-secret-key"
    cors_origins_raw: str = Field(
        default="http://localhost:8501,http://localhost:3000,https://weather-forecast.vercel.app",
        alias="CORS_ORIGINS",
    )

    # Rate Limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Log Retention (50MB Max)
    log_max_bytes: int = 10 * 1024 * 1024  # 10 MB
    log_backup_count: int = 5  # 5 files max = 50MB

    # Scheduler Settings
    schedule_cron_hour: int = 6
    schedule_cron_minute: int = 0
    auto_train_enabled: bool = True

    # Database Settings
    sqlite_db_path: str = "artifacts/weather_history.db"
    db_retention_days: int = 30

    @property
    def cors_origins(self) -> List[str]:
        """Chuyển chuỗi origins phân tách bằng dấu phẩy thành danh sách."""
        if isinstance(self.cors_origins_raw, list):
            return self.cors_origins_raw
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )


@lru_cache()
def get_settings() -> Settings:
    """Singleton pattern nạp settings từ môi trường."""
    return Settings()


settings = get_settings()
