"""
Database Connection Pool

This module provides connection pooling functionality for the MCP system.
It includes:

1. Connection pool configuration and management
2. Pool statistics and monitoring
3. Connection health checks
4. Pool size optimization
"""

import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Database connection pool manager.

    This class provides:
    1. Connection pool management
    2. Pool statistics
    3. Connection health monitoring
    4. Automatic pool size adjustment
    """

    def __init__(
        self,
        url: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
    ):
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
        self.url = url or os.getenv("DATABASE_URL", "sqlite:///./mcp.db")
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping

        # Create engine with connection pool
        self.engine = create_engine(
            self.url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
        )

        # Create session factory
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

        logger.info(
            f"Initialized database pool with size {pool_size}, "
            f"max overflow {max_overflow}, timeout {pool_timeout}s"
        )

    @contextmanager
    def get_session(self):
        """
        Get a database session from the pool.

        Yields:
            Session: Database session
        """
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def get_pool_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.

        Returns:
            Dict[str, Any]: Pool statistics
        """
        try:
            return {
                "size": self.pool_size,
                "checkedin": self.engine.pool.checkedin(),
                "checkedout": self.engine.pool.checkedout(),
                "overflow": self.engine.pool.overflow(),
                "checkedin_connections": len(self.engine.pool._pool),
                "max_overflow": self.max_overflow,
                "timeout": self.pool_timeout,
                "recycle": self.pool_recycle,
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {str(e)}")
            return {}

    def optimize_pool_size(self, target_utilization: float = 0.8) -> None:
        """
        Optimize pool size based on current usage.

        Args:
            target_utilization: Target pool utilization (0.0 to 1.0)
        """
        try:
            stats = self.get_pool_stats()
            current_utilization = stats["checkedout"] / (stats["size"] + stats["overflow"])

            if current_utilization > target_utilization:
                # Increase pool size if utilization is too high
                new_size = int(stats["size"] * 1.5)
                self.resize_pool(new_size)
                logger.info(f"Increased pool size to {new_size} due to high utilization")
            elif current_utilization < target_utilization * 0.5:
                # Decrease pool size if utilization is too low
                new_size = max(1, int(stats["size"] * 0.75))
                self.resize_pool(new_size)
                logger.info(f"Decreased pool size to {new_size} due to low utilization")

        except Exception as e:
            logger.error(f"Error optimizing pool size: {str(e)}")

    def resize_pool(self, new_size: int) -> None:
        """
        Resize the connection pool.

        Args:
            new_size: New pool size
        """
        try:
            # Create new engine with updated pool size
            new_engine = create_engine(
                self.url,
                poolclass=QueuePool,
                pool_size=new_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=self.pool_pre_ping,
            )

            # Update session factory
            self.SessionFactory = sessionmaker(bind=new_engine, expire_on_commit=False)

            # Close old engine
            self.engine.dispose()

            # Update engine and pool size
            self.engine = new_engine
            self.pool_size = new_size

            logger.info(f"Resized connection pool to {new_size}")

        except Exception as e:
            logger.error(f"Error resizing pool: {str(e)}")
            raise

    def check_connection_health(self) -> bool:
        """
        Check the health of a test connection.

        Returns:
            bool: True if connection is healthy
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Connection health check failed: {str(e)}")
            return False
