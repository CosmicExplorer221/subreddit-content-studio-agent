"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "LinkedIn Content Automation"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Storage
    data_path: str = "data"

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # API Keys (optional - will be added when integrations are implemented)
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    gemini_api_key: Optional[str] = None
    notion_api_token: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
