from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class MCPConfig(BaseSettings):
    """Configuration for MCP application."""

    api_base_url: str = Field(default="http://localhost:8000")
    api_key: str = Field(default="your-api-key-here")
    debug: bool = Field(default=False)

    # File paths
    notebooks_dir: str = Field(default="mcp/notebooks")
    scripts_dir: str = Field(default="mcp/scripts")

    # Timeouts
    default_timeout: int = Field(default=600)  # 10 minutes
    websocket_timeout: int = Field(default=30)

    # Retry settings
    max_retries: int = Field(default=3)
    retry_delay: int = Field(default=1)

    class Config:
        env_prefix = "MCP_"
        case_sensitive = False


# Create global config instance
config = MCPConfig()
