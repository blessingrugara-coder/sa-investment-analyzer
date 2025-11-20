"""Application settings"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database
    database_url: str = "sqlite:///sa_investments.db"
    
    # API Keys
    openbb_api_key: Optional[str] = None
    alpha_vantage_key: Optional[str] = None
    
    # Scraping
    user_agent: str = "SA-Investment-Analyzer/1.0"
    max_requests_per_minute: int = 10
    scraping_delay_seconds: float = 6.0
    enable_cache: bool = True
    cache_expiry_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_max_bytes: int = 10485760
    log_backup_count: int = 5
    
    # Scheduler
    enable_auto_updates: bool = True
    update_hour: int = 18
    update_timezone: str = "Africa/Johannesburg"
    
    @property
    def cache_dir(self) -> str:
        return "data/cache"


settings = Settings()