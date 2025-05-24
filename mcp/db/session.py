"""
Database Session Management

This module provides database session management functionality for the MCP system.
It handles:

1. Session factory configuration
2. Connection pooling
3. Transaction management
4. Context managers for session handling
5. Error handling and recovery

The module uses SQLAlchemy for database operations and provides utilities
for managing database sessions in a thread-safe manner.
"""

import os
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import logging

from .models import Base
from .base_models import get_database_url

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

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    This function:
    1. Creates a new database session
    2. Handles transaction management
    3. Ensures proper cleanup
    4. Provides error handling
    
    Usage:
        ```python
        with get_db() as db:
            # Use the database session
            result = db.query(Model).all()
        ```
    
    Yields:
        Session: A SQLAlchemy database session
    
    Raises:
        Exception: If there's an error with the database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get a new database session.
    
    This function:
    1. Creates a new session
    2. Configures session settings
    3. Returns the session
    
    Note: The caller is responsible for closing the session.
    
    Returns:
        Session: A SQLAlchemy database session
    """
    return SessionLocal()

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