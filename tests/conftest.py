import pytest
import os
from mcp.api.client import MCPClient
from mcp.db.session import SessionLocal
from mcp.cache.redis_manager import RedisCacheManager

# Test API key
TEST_API_KEY = "test-api-key"

@pytest.fixture(scope="session")
def api_client():
    """Create an API client for testing."""
    os.environ["MCP_API_KEY"] = TEST_API_KEY
    return MCPClient()

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def redis_client():
    """Create a Redis client for testing."""
    client = RedisCacheManager()
    try:
        yield client
    finally:
        # Clean up test keys
        client.delete("test_key")
        client.delete_hash("test_hash") 