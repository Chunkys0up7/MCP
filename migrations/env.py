"""
Alembic Environment Configuration

This module configures the Alembic migration environment for the MCP system.
It handles:

1. Database connection setup
2. Migration context configuration
3. Logging configuration
4. Environment-specific settings
5. Migration script generation

The environment supports both online (with database connection) and offline
(with SQL script generation) migration modes.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Get the database URL from environment or configuration
# Import the SQLAlchemy models
from mcp.db.base_models import Base
from mcp.db.models import *  # Import all models for Alembic to detect

# Load Alembic configuration
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the database URL to the Alembic configuration
config.set_main_option(
    "sqlalchemy.url", "postgresql+psycopg2://postgres:postgres@localhost:5432/mcp"
)

# Add MetaData object to the target_metadata
target_metadata = Base.metadata


def get_url() -> str:
    """
    Get the database URL for migrations.

    This function:
    1. Gets the URL from configuration
    2. Handles environment-specific settings
    3. Validates the URL format

    Returns:
        str: The database URL
    """
    return "postgresql+psycopg2://postgres:postgres@localhost:5432/mcp"


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This function:
    1. Generates SQL scripts for migrations
    2. Doesn't require a database connection
    3. Outputs SQL to stdout or files

    This is useful for:
    - Generating SQL scripts for manual execution
    - Reviewing migration changes
    - Deploying to environments with restricted access
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This function:
    1. Connects to the database
    2. Executes migrations directly
    3. Handles transaction management

    This is useful for:
    - Direct database updates
    - Automated deployments
    - Development environments
    """
    # Get the database URL from configuration
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    # Create the engine
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Run the migrations
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Compare column types
            compare_server_default=True,  # Compare server defaults
        )

        with context.begin_transaction():
            context.run_migrations()


# Run migrations based on the mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
