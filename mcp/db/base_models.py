"""
Base Database Models

This module provides the base SQLAlchemy models and utilities for the MCP system.
It includes:

1. Base model class with common functionality
2. Timestamp mixin for created/updated tracking
3. UUID primary key mixin
4. Common model utilities and helpers
"""

import os
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import (JSON, CheckConstraint, Column, DateTime, ForeignKey,
                        Integer, String, create_engine)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (Mapped, mapped_column, registry, relationship,
                            sessionmaker)

mapper_registry = registry()
Base = mapper_registry.generate_base()


class TimestampMixin:
    """
    Mixin class that adds created_at and updated_at timestamp columns to models.

    This mixin automatically:
    1. Sets created_at when a record is first created
    2. Updates updated_at whenever a record is modified

    Example:
        ```python
        class MyModel(Base, TimestampMixin):
            __tablename__ = 'my_model'
            id = Column(UUID(as_uuid=True), primary_key=True)
            # created_at and updated_at are automatically added
        ```
    """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UUIDMixin:
    """
    Mixin class that adds a UUID primary key column to models.

    This mixin:
    1. Adds a UUID primary key column
    2. Automatically generates UUIDs for new records
    3. Uses PostgreSQL's native UUID type

    Example:
        ```python
        class MyModel(Base, UUIDMixin):
            __tablename__ = 'my_model'
            # id is automatically added as UUID primary key
        ```
    """

    id: Mapped[Any] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model class that combines common functionality for all models.

    This class provides:
    1. UUID primary key
    2. Created/updated timestamps
    3. Common model methods and utilities

    All models should inherit from this class to get the common functionality.

    Example:
        ```python
        class MyModel(BaseModel):
            __tablename__ = 'my_model'
            # Gets id, created_at, updated_at automatically
        ```
    """

    __abstract__ = True
    __allow_unmapped__ = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        This method:
        1. Gets all column values
        2. Converts datetime objects to ISO format strings
        3. Converts UUID objects to strings

        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid4):
                value = str(value)
            result[column.name] = value
        return result

    def update(self, **kwargs) -> None:
        """
        Update the model instance with the given values.

        This method:
        1. Updates only the provided fields
        2. Validates the values against column types
        3. Triggers the updated_at timestamp update

        Args:
            **kwargs: Field names and values to update

        Raises:
            ValueError: If an invalid field name is provided
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Invalid field name: {key}")
            setattr(self, key, value)


def get_database_url() -> str:
    """
    Get the database URL from environment variables or use a default SQLite URL.

    Returns:
        str: The database URL to use for the SQLAlchemy engine.
    """
    return os.getenv("DATABASE_URL", "sqlite:///./mcp.db")


def create_db_engine():
    """
    Create and configure the SQLAlchemy engine.

    Returns:
        Engine: A configured SQLAlchemy engine instance.
    """
    return create_engine(
        get_database_url(),
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        pool_pre_ping=True,
        pool_recycle=3600,
    )


def get_db_session():
    """
    Create a new database session.

    Returns:
        Session: A new SQLAlchemy session instance.
    """
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def init_db():
    """
    Initialize the database by creating all tables.

    This function should be called when the application starts to ensure
    all required database tables exist.
    """
    engine = create_db_engine()
    Base.metadata.create_all(bind=engine)


class MCPConfiguration(BaseModel):
    """Model for storing MCP configurations."""

    __tablename__ = "mcp_configurations"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    dependencies: Mapped[dict] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        CheckConstraint("type IN ('prompt', 'notebook', 'data')", name="valid_mcp_type"),
    )


class MCPChain(BaseModel):
    """Model for storing MCP chains."""

    __tablename__ = "mcp_chains"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    workflow: Mapped[dict] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_chain: Mapped[Any] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mcp_chains.id"), nullable=True
    )

    # Relationships
    parent = relationship("MCPChain", remote_side="MCPChain.id", back_populates="child_chains")
    child_chains = relationship("MCPChain", back_populates="parent", cascade="all, delete-orphan")


class ChainSession(BaseModel):
    """Model for storing chain execution sessions."""

    __tablename__ = "chain_sessions"

    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    chain_data: Mapped[dict] = mapped_column(JSON, nullable=False)


class MCPPermission(BaseModel):
    """Model for storing MCP access permissions."""

    __tablename__ = "mcp_permissions"

    user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), primary_key=True)
    chain_id: Mapped[Any] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mcp_chains.id"), primary_key=True
    )
    access_level: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (CheckConstraint("access_level IN (1, 2, 3)", name="valid_access_level"),)


class AuditLog(BaseModel):
    """Model for storing audit logs."""

    __tablename__ = "audit_logs"

    user_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[Any] = mapped_column(UUID(as_uuid=True), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=True)


def log_audit_action(db, user_id, action_type, target_id, details=None):
    """Insert an audit log entry."""
    from mcp.db.models import AuditLog

    log = AuditLog(
        user_id=user_id, action_type=action_type, target_id=target_id, details=details or {}
    )
    db.add(log)
    db.commit()
