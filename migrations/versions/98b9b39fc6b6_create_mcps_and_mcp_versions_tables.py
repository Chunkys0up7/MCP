"""Create MCPs and MCP versions tables

Revision ID: 98b9b39fc6b6
Revises: 20240321_initial
Create Date: 2025-05-22 15:41:08.147239+00:00

This migration adds support for MCPs (Model Context Protocols) and their versions
by creating two new tables:
1. mcps - Stores MCP definitions with their metadata and configuration
2. mcp_versions - Stores versioned configurations for each MCP

The tables use UUID primary keys and include appropriate indexes for efficient
querying. The mcp_versions table has a foreign key relationship to mcps.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "98b9b39fc6b6"
down_revision = "20240321_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create MCPs and MCP versions tables.

    This function creates two new tables:
    1. mcps:
       - Stores MCP definitions with their metadata
       - Uses UUID primary key
       - Includes indexes for type and tags
       - Includes vector embedding for semantic search

    2. mcp_versions:
       - Stores versioned configurations for each MCP
       - Uses UUID primary key
       - Has foreign key to mcps
       - Includes unique constraint on mcp_id and version
    """
    # Create mcps table
    op.create_table(
        "mcps",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("initial_config", sa.JSON(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("embedding", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_mcp_type", "mcps", ["type"])

    # Create mcp_versions table
    op.create_table(
        "mcp_versions",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("mcp_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["mcp_id"], ["mcps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_mcp_version", "mcp_versions", ["mcp_id", "version"], unique=True
    )


def downgrade() -> None:
    """
    Remove MCPs and MCP versions tables.

    This function drops the mcp_versions and mcps tables in the correct
    order to handle the foreign key dependency.
    """
    op.drop_table("mcp_versions")
    op.drop_table("mcps")
