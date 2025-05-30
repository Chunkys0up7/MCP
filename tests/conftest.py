import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp.api.client import MCPClient
from mcp.api.main import app  # Your FastAPI app
# from mcp.db.session import SessionLocal # This is for PostgreSQL
from mcp.cache.redis_manager import RedisCacheManager
# Import Base from your models file to create/drop tables
from mcp.db.models import Base  # Adjust this import if your Base is elsewhere
from mcp.db.session import get_db_session  # Original get_db

# Test API key
TEST_API_KEY = "test-api-key"

# --- Test Database Setup (file-based SQLite) ---
TEST_DB_PATH = "./test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"


def remove_test_db():
    try:
        os.remove(TEST_DB_PATH)
    except FileNotFoundError:
        pass


# Remove test.db before the test session starts
remove_test_db()

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # check_same_thread is for SQLite
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Fixture to create and drop tables for each test function
@pytest.fixture(scope="function")
def test_db_session():
    Base.metadata.create_all(bind=test_engine)  # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)  # Drop tables after test


# Remove test.db after the test session ends
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    remove_test_db()


# Fixture to override the 'get_db_session' dependency in the FastAPI app
@pytest.fixture(
    scope="function"
)  # Or "session" if you want the override for the whole session
def override_get_db(test_db_session):  # Depends on the test_db_session fixture
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            test_db_session.close()  # Ensure session is closed, though test_db_session fixture already does.

    app.dependency_overrides[get_db_session] = _override_get_db
    yield
    app.dependency_overrides.clear()  # Clear overrides after test


# --- Original Fixtures (keeping them as they might be used or adapted) ---


@pytest.fixture(scope="session")
def api_client():
    """Create an API client for testing."""
    os.environ["MCP_API_KEY"] = TEST_API_KEY
    return MCPClient()


# This db_session fixture now refers to the PostgreSQL session.
# For tests requiring DB interaction via TestClient, the override_get_db should be used.
@pytest.fixture(scope="function")
def db_session_postgres():  # Renamed to avoid confusion
    """Create a PostgreSQL database session for testing (if needed for direct DB tests not via API)."""
    # This uses the original SessionLocal which points to PostgreSQL configured in mcp/db/session.py
    from mcp.db.session import SessionLocal as PostgresSessionLocal

    session = PostgresSessionLocal()
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


# Fixture for TestClient that uses the overridden DB
@pytest.fixture(scope="function")
def test_app_client(override_get_db):  # Depends on the override_get_db fixture
    # Set the API key in environment before creating TestClient
    os.environ["MCP_API_KEY"] = TEST_API_KEY
    # The override_get_db fixture ensures that app.dependency_overrides[get_db] is set
    # before the TestClient is created and yielded.
    with TestClient(app) as c:
        yield c
