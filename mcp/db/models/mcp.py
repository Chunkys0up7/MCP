from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # For PostgreSQL UUID type
import uuid # For default factory

from ..base_models import Base # Changed import
from mcp.core.types import MCPType # For Enum type in DB (SQLAlchemy handles this)

class MCP(Base):
    __tablename__ = "mcp__mcps"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    # For MCPType, store as string. SQLAlchemy can handle Enum directly too.
    type = Column(String(50), nullable=False, index=True) # Store enum as string
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True) # Store list of strings as JSON array

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    versions = relationship("MCPVersion", back_populates="mcp", cascade="all, delete-orphan")
    # latest_version_id = Column(PG_UUID(as_uuid=True), ForeignKey("mcp__mcp_versions.id"), nullable=True) # Optional: direct link to latest version
    # latest_version = relationship("MCPVersion", foreign_keys=[latest_version_id])

class MCPVersion(Base):
    __tablename__ = "mcp__mcp_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mcp_id = Column(PG_UUID(as_uuid=True), ForeignKey("mcp__mcps.id"), nullable=False, index=True)
    
    version_str = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    config_snapshot = Column(JSON, nullable=False) # Store config as JSON
    # manifest_hash = Column(String(64), nullable=True, index=True) # e.g., SHA256

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    mcp = relationship("MCP", back_populates="versions")

    __table_args__ = (
        # Unique constraint for mcp_id and version_str to ensure a version is unique per MCP
        # Consider if 'latest' or other special tags for version_str need different handling
        # If version_str can be non-unique for things like 'latest' pointing to different actual versions over time,
        # then this unique constraint might be too strict or need adjustment.
        # For now, assuming version_str should be unique per mcp_id.
        # sqlalchemy.schema.UniqueConstraint('mcp_id', 'version_str', name='uq_mcp_version_str'),
    )

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