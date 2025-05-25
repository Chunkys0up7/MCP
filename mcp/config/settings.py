import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="mcp", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="postgres", env="DB_PASSWORD")
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=1800, env="DB_POOL_RECYCLE")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    file: Optional[str] = Field(default=None, env="LOG_FILE")


class StreamlitSettings(BaseSettings):
    """Streamlit configuration settings."""

    theme: Dict[str, Any] = Field(
        default={
            "primaryColor": "#FF4B4B",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F0F2F6",
            "textColor": "#262730",
            "font": "sans serif",
        },
        env="STREAMLIT_THEME",
    )
    page_title: str = Field(default="MCP Builder", env="STREAMLIT_PAGE_TITLE")
    page_icon: str = Field(default="🤖", env="STREAMLIT_PAGE_ICON")


class Settings(BaseSettings):
    """Main application settings."""

    # Base settings
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Application settings
    app_name: str = Field(default="MCP Builder", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")

    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    streamlit: StreamlitSettings = StreamlitSettings()

    # File paths
    base_dir: Path = Path(__file__).parent.parent.parent
    static_dir: Path = base_dir / "static"
    templates_dir: Path = base_dir / "templates"
    uploads_dir: Path = base_dir / "uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment variables


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def update_settings(**kwargs) -> None:
    """Update settings with new values."""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


def load_env_file(env_file: str = ".env") -> None:
    """Load environment variables from a file."""
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
