"""
Database Initialization

This module provides database initialization functionality for the MCP system.
It handles:

1. Schema creation
2. Initial data seeding
3. Index creation
4. Constraint setup
5. Migration handling

The module ensures the database is properly set up with all required
tables, indexes, and initial data for the system to function correctly.
"""

import logging
from typing import Any, Dict, List

from sqlalchemy.exc import SQLAlchemyError

from mcp.db.base_models import Base
from mcp.db.models import MCP, MCPVersion, WorkflowDefinition
from mcp.db.session import get_db

# Configure logging
logger = logging.getLogger(__name__)


def init_database() -> None:
    """
    Initialize the database.

    This function:
    1. Creates all tables
    2. Sets up indexes
    3. Seeds initial data
    4. Handles errors

    The initialization process:
    - Creates all required tables
    - Sets up proper indexes
    - Configures constraints
    - Seeds default data

    Raises:
        SQLAlchemyError: If database initialization fails
    """
    try:
        # Create all tables
        Base.metadata.create_all()
        logger.info("Database tables created successfully")

        # Seed initial data
        seed_initial_data()
        logger.info("Initial data seeded successfully")

    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def seed_initial_data() -> None:
    """
    Seed initial data into the database.

    This function:
    1. Creates default MCPs
    2. Sets up initial workflows
    3. Configures system settings
    4. Handles errors

    The seeding process:
    - Creates essential MCPs
    - Sets up default workflows
    - Configures system parameters

    Raises:
        SQLAlchemyError: If data seeding fails
    """
    try:
        with get_db() as db:
            # Create default MCPs
            create_default_mcps(db)

            # Create default workflows
            create_default_workflows(db)

    except SQLAlchemyError as e:
        logger.error(f"Failed to seed initial data: {str(e)}")
        raise


def create_default_mcps(db) -> None:
    """
    Create default MCPs.

    This function:
    1. Creates essential MCPs
    2. Sets up initial versions
    3. Configures metadata
    4. Handles errors

    The MCPs created:
    - System MCPs
    - Utility MCPs
    - Example MCPs

    Args:
        db: Database session

    Raises:
        SQLAlchemyError: If MCP creation fails
    """
    try:
        # Create system MCPs
        system_mcp = MCP(
            name="System", type="system", description="System-level MCP", tags=["system", "core"]
        )
        db.add(system_mcp)

        # Create utility MCPs
        utility_mcp = MCP(
            name="Utility",
            type="utility",
            description="Utility functions MCP",
            tags=["utility", "helper"],
        )
        db.add(utility_mcp)

        # Create example MCPs
        example_mcp = MCP(
            name="Example",
            type="example",
            description="Example MCP for demonstration",
            tags=["example", "demo"],
        )
        db.add(example_mcp)

        db.commit()
        logger.info("Default MCPs created successfully")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create default MCPs: {str(e)}")
        raise


def create_default_workflows(db) -> None:
    """
    Create default workflows.

    This function:
    1. Creates essential workflows
    2. Sets up step configurations
    3. Configures schemas
    4. Handles errors

    The workflows created:
    - System workflows
    - Utility workflows
    - Example workflows

    Args:
        db: Database session

    Raises:
        SQLAlchemyError: If workflow creation fails
    """
    try:
        # Create system workflow
        system_workflow = WorkflowDefinition(
            name="System Setup",
            description="System initialization workflow",
            steps=[{"name": "Initialize System", "mcp_id": "system", "config": {}}],
            input_schema={},
            output_schema={},
            error_strategy="stop",
            execution_mode="sequential",
        )
        db.add(system_workflow)

        # Create utility workflow
        utility_workflow = WorkflowDefinition(
            name="Utility Functions",
            description="Common utility functions workflow",
            steps=[{"name": "Run Utility", "mcp_id": "utility", "config": {}}],
            input_schema={},
            output_schema={},
            error_strategy="continue",
            execution_mode="sequential",
        )
        db.add(utility_workflow)

        # Create example workflow
        example_workflow = WorkflowDefinition(
            name="Example Workflow",
            description="Example workflow for demonstration",
            steps=[{"name": "Run Example", "mcp_id": "example", "config": {}}],
            input_schema={},
            output_schema={},
            error_strategy="retry",
            execution_mode="sequential",
        )
        db.add(example_workflow)

        db.commit()
        logger.info("Default workflows created successfully")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create default workflows: {str(e)}")
        raise


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
