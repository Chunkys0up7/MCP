from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class MCPConfiguration(Base):
    """Model for storing MCP configurations."""
    __tablename__ = "mcp_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    config = Column(JSONB, nullable=False)
    dependencies = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "type IN ('prompt', 'notebook', 'data')",
            name="valid_mcp_type"
        ),
    )

class MCPChain(Base):
    """Model for storing MCP chains."""
    __tablename__ = "mcp_chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, nullable=False)
    workflow = Column(JSONB, nullable=False)
    version = Column(Integer, default=1)
    parent_chain = Column(UUID(as_uuid=True), ForeignKey("mcp_chains.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    parent = relationship("MCPChain", remote_side=[id], backref="child_chains")

class ChainSession(Base):
    """Model for storing chain execution sessions."""
    __tablename__ = "chain_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), unique=True, nullable=False)
    chain_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_activity = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class MCPPermission(Base):
    """Model for storing MCP access permissions."""
    __tablename__ = "mcp_permissions"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    chain_id = Column(UUID(as_uuid=True), ForeignKey("mcp_chains.id"), primary_key=True)
    access_level = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "access_level BETWEEN 1 AND 3",
            name="valid_access_level"
        ),
    )

class AuditLog(Base):
    """Model for storing audit logs."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    details = Column(JSONB)
 