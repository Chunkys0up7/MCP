"""
Database Session Management

This module provides database session management using connection pooling.
It includes:

1. Session factory configuration
2. Connection pool management
3. Session lifecycle handling
4. Error handling and retries
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .base_models import get_database_url
from .models import Base
from .pool import DatabasePool

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mcp")

# Create database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Maximum number of connections to keep
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Global connection pool instance
_pool: Optional[DatabasePool] = None


def init_pool(
    url: Optional[str] = None,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    pool_pre_ping: bool = True,
) -> None:
    """
    Initialize the database connection pool.

    Args:
        url: Database URL (uses DATABASE_URL env var if None)
        pool_size: Number of connections to keep open
        max_overflow: Maximum number of connections that can be created beyond pool_size
        pool_timeout: Seconds to wait before giving up on getting a connection
        pool_recycle: Seconds after which a connection is automatically recycled
        pool_pre_ping: Whether to check connection health before using it
    """
    global _pool
    if _pool is None:
        _pool = DatabasePool(
            url=url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
        )
        logger.info("Initialized database connection pool")


def get_pool() -> DatabasePool:
    """
    Get the database connection pool.

    Returns:
        DatabasePool: The connection pool instance

    Raises:
        RuntimeError: If pool is not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return _pool


@contextmanager
def get_db_session() -> Session:
    """
    Get a database session from the pool.

    Yields:
        Session: Database session

    Raises:
        RuntimeError: If pool is not initialized
    """
    pool = get_pool()
    with pool.get_session() as session:
        yield session


def get_pool_stats() -> dict:
    """
    Get connection pool statistics.

    Returns:
        dict: Pool statistics

    Raises:
        RuntimeError: If pool is not initialized
    """
    pool = get_pool()
    return pool.get_pool_stats()


def optimize_pool_size(target_utilization: float = 0.8) -> None:
    """
    Optimize pool size based on current usage.

    Args:
        target_utilization: Target pool utilization (0.0 to 1.0)

    Raises:
        RuntimeError: If pool is not initialized
    """
    pool = get_pool()
    pool.optimize_pool_size(target_utilization)


def check_connection_health() -> bool:
    """
    Check the health of a test connection.

    Returns:
        bool: True if connection is healthy

    Raises:
        RuntimeError: If pool is not initialized
    """
    pool = get_pool()
    return pool.check_connection_health()


def init_db() -> None:
    """
    Initialize the database.

    This function:
    1. Creates all tables
    2. Sets up indexes
    3. Configures constraints
    4. Handles errors

    Raises:
        Exception: If database initialization fails
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def get_connection_pool():
    """Get the database connection pool."""
    return engine.pool
