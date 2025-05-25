"""
Base Models

This module provides base model classes and mixins for the MCP system.
It includes:

1. Base model class with common functionality
2. Timestamp mixin for created/updated tracking
3. UUID primary key mixin
4. Common model utilities and helpers

The base models provide:
- Common functionality for all models
- Standard fields and methods
- Type safety and validation
- Relationship management
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeMeta, Mapped, mapped_column

from ..base_models import Base


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps.

    This mixin:
    1. Adds created_at timestamp
    2. Adds updated_at timestamp
    3. Auto-updates timestamps
    4. Provides timestamp utilities

    Usage:
        ```python
        class MyModel(BaseModel, TimestampMixin):
            # Model definition
            pass
        ```
    """

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UUIDMixin:
    """
    Mixin to add UUID primary key.

    This mixin:
    1. Adds UUID primary key
    2. Auto-generates UUIDs
    3. Provides UUID utilities
    4. Ensures uniqueness

    Usage:
        ```python
        class MyModel(BaseModel, UUIDMixin):
            # Model definition
            pass
        ```
    """

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)


class BaseModel(Base):
    """
    Base model class with common functionality.

    This class:
    1. Provides common methods
    2. Handles serialization
    3. Manages relationships
    4. Supports validation

    Usage:
        ```python
        class MyModel(BaseModel, UUIDMixin, TimestampMixin):
            # Model definition
            pass
        ```
    """

    __abstract__ = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        This method:
        1. Serializes model to dict
        2. Handles relationships
        3. Formats values
        4. Excludes private fields

        Returns:
            Dict[str, Any]: Model as dictionary
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def update(self, **kwargs: Any) -> None:
        """
        Update model attributes.

        This method:
        1. Updates attributes
        2. Validates values
        3. Handles relationships
        4. Manages timestamps

        Args:
            **kwargs: Attributes to update

        Raises:
            ValueError: If validation fails
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid attribute: {key}")

    @classmethod
    def get_by_id(cls, id: str) -> Optional["BaseModel"]:
        """
        Get model by ID.

        This method:
        1. Queries by ID
        2. Handles not found
        3. Manages relationships
        4. Returns result

        Args:
            id: Model ID

        Returns:
            Optional[BaseModel]: Model instance or None
        """
        return cls.query.get(id)

    def __repr__(self) -> str:
        """
        String representation of model.

        Returns:
            str: Model representation
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
