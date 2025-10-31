"""
Configuration settings loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Lightning AI
    lightning_ai_api_key: str
    lightning_ai_url: str = "https://lightning.ai/api/v1/chat/completions"
    lightning_ai_model: str = "openai/gpt-4-turbo"
    
    # LiveKit
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    
    # Firebase
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_database_url: str
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    log_level: str = "INFO"
    
    # Timeouts
    help_request_timeout: int = 3600  # 1 hour in seconds
    supervisor_notification_retry: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()