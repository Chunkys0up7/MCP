"""
Database Models

This package contains all database models for the MCP system.
It includes:

1. MCP and version models
2. Workflow definition and execution models
3. Base model classes
4. Model relationships
5. Model utilities

The models are designed to:
- Support version control
- Enable workflow execution
- Track execution history
- Handle data validation
- Manage relationships
"""

# Import Base and other models from base_models.py
from ..base_models import (AuditLog, Base, ChainSession, MCPChain,
                           MCPConfiguration, MCPPermission)
from .base import BaseModel, TimestampMixin, UUIDMixin
# Import the new MCP and MCPVersion models
from .mcp import MCP, MCPVersion
from .review import Review
from .user import User
from .workflow import WorkflowDefinition, WorkflowRun, WorkflowStepRun

# Define what gets imported with 'from .models import *'
__all__ = [
    # Base models
    "Base",
    "MCPConfiguration",
    "MCPChain",
    "ChainSession",
    "MCPPermission",
    "AuditLog",
    # MCP models
    "MCP",
    "MCPVersion",
    # Workflow models
    "WorkflowDefinition",
    "WorkflowRun",
    "WorkflowStepRun",
    # Base model classes
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "Review",
    "User",
]
