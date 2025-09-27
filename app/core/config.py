from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration with enhanced AI provider support"""

    # Application
    app_name: str = "Lead Scoring API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # AI Services - Multi-provider with cost optimization
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    ai_primary_provider: str = "gemini"  # Try free Gemini first
    ai_fallback_enabled: bool = True
    ai_max_retries: int = 2
    ai_timeout: int = 15  # Shorter timeout for faster fallback

    # AI Model Configuration
    gemini_model: str = "gemini-1.5-flash"  # Free tier model
    openai_model: str = "gpt-4o-mini"       # Cheaper OpenAI model

    # Business Logic
    max_leads_per_upload: int = 1000
    max_file_size_mb: int = 10

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()