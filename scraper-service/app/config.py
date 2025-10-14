"""
Configuration management for scraper service
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://ignition:ignition@postgres:5432/exchange_scraper"
    )

    # Scraper settings
    base_url: str = "https://inductiveautomation.com/exchange/"
    headless: bool = True
    nav_timeout: int = 60000  # milliseconds
    selector_timeout: int = 15000  # milliseconds
    load_more_attempts: int = 100

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Timezone
    timezone: str = "Australia/Adelaide"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
