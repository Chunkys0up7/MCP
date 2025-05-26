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

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...schemas.mcp import MCPStatus, MCPType
from ..base_models import Base

# Association table for MCP tags
mcp_tags = Table(
    "mcp_tags",
    Base.metadata,
    Column("mcp_id", UUID(as_uuid=True), ForeignKey("mcps.id")),
    Column("tag", String),
)


class MCP(Base):
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(Enum(MCPType), nullable=False)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("mcp_versions.id"))
    # tags = relationship('Tag', secondary=mcp_tags, backref='mcps')  # Commented out: Tag model not defined
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship(
        "MCPVersion", back_populates="mcp", foreign_keys="MCPVersion.mcp_id"
    )
    current_version = relationship("MCPVersion", foreign_keys=[current_version_id])


class MCPVersion(Base):
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
    """

    __tablename__ = "mcp_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_id = Column(UUID(as_uuid=True), ForeignKey("mcps.id"), nullable=False)
    version = Column(String, nullable=False)
    definition = Column(JSON, nullable=False)
    status = Column(Enum(MCPStatus), default=MCPStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mcp = relationship("MCP", back_populates="versions", foreign_keys=[mcp_id])


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
