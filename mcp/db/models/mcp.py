"""
MCP Database Models

This module defines the SQLAlchemy models for storing MCP (Model Context Protocol)
definitions and their versions in the database. These models are used to track
the evolution of MCPs over time and maintain their metadata.

The models support:
1. Version control of MCP definitions
2. Metadata tracking (creation, modification, status)
3. Tag-based categorization
4. Input/output schema validation
5. Configuration management
"""

from uuid import UUID as PyUUID
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Enum, ForeignKey, String, Table, DateTime, Column
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...schemas.mcp import MCPStatus, MCPType
from ..base_models import Base

# Association table for MCP tags
mcp_tags = Table(
    "mcp_tags",
    Base.metadata,
    Column("mcp_id", SA_UUID(as_uuid=True), ForeignKey("mcps.id")),
    Column("tag", String),
)


class MCP(Base):  # type: ignore[misc, valid-type]
    """
    Represents a Model Context Protocol (MCP) definition in the database.

    An MCP is a reusable component that defines:
    1. Input/output schemas
    2. Configuration parameters
    3. Implementation details
    4. Metadata and versioning

    Attributes:
        id (UUID): Unique identifier for the MCP
        name (str): Human-readable name of the MCP
        description (str): Detailed description of the MCP's purpose and functionality
        type (MCPType): Type of the MCP (e.g., PYTHON_SCRIPT, API_ENDPOINT)
        current_version_id (UUID): ID of the current active version
        tags (List[str]): List of tags for categorization
        created_at (datetime): When the MCP was created
        updated_at (datetime): When the MCP was last updated
        versions (List[MCPVersion]): List of all versions of this MCP
        current_version (MCPVersion): The current active version
    """

    __tablename__ = "mcps"

    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[MCPType] = mapped_column(Enum(MCPType), nullable=False)
    current_version_id: Mapped[PyUUID | None] = mapped_column(SA_UUID(as_uuid=True), ForeignKey("mcp_versions.id"), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    embedding: Mapped[dict] = mapped_column(JSON, nullable=True)
    # tags = relationship('Tag', secondary=mcp_tags, backref='mcps')  # Commented out: Tag model not defined
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions: Mapped[list["MCPVersion"]] = relationship(
        "MCPVersion", back_populates="mcp", foreign_keys="MCPVersion.mcp_id"
    )
    current_version: Mapped[Optional["MCPVersion"]] = relationship("MCPVersion", foreign_keys=[current_version_id])


class MCPVersion(Base):  # type: ignore[misc, valid-type]
    """
    Represents a specific version of an MCP definition.

    Each version contains:
    1. The complete MCP definition
    2. Input/output schemas
    3. Configuration parameters
    4. Implementation details
    5. Status and metadata

    Attributes:
        id (UUID): Unique identifier for the version
        mcp_id (UUID): ID of the parent MCP
        version (str): Version number (e.g., "1.0.0")
        definition (dict): Complete MCP definition including:
            - input_schema: JSON Schema for inputs
            - output_schema: JSON Schema for outputs
            - config_schema: JSON Schema for configuration
            - implementation: Implementation details
        status (MCPStatus): Current status (e.g., DRAFT, ACTIVE, DEPRECATED)
        created_at (datetime): When the version was created
        updated_at (datetime): When the version was last updated
        mcp (MCP): Reference to the parent MCP
        version_str (str): Version string
        description (str): Description of the version
        config_snapshot (dict): Configuration snapshot
    """

    __tablename__ = "mcp_versions"

    id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_id: Mapped[PyUUID] = mapped_column(SA_UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[MCPStatus] = mapped_column(Enum(MCPStatus), default=MCPStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version_str: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    config_snapshot: Mapped[dict] = mapped_column(JSON, nullable=True)

    mcp: Mapped["MCP"] = relationship("MCP", back_populates="versions", foreign_keys=[mcp_id])


# Ensure mcp.db.base_class.Base is correctly defined, e.g.:
# from sqlalchemy.ext.declarative import as_declarative, declared_attr
# @as_declarative()
# class Base:
#     id: Any
#     __name__: str
#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()
