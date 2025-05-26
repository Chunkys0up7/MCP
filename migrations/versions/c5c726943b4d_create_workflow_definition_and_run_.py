"""Create workflow definition and execution tables

Revision ID: c5c726943b4d
Revises: 98b9b39fc6b6
Create Date: 2025-05-22 21:28:13.308320+00:00

This migration adds support for workflow definitions and executions by creating
two new tables:
1. workflow_definitions - Stores workflow definitions with their steps and metadata
2. workflow_runs - Stores workflow execution records with their status and results

The tables use UUID primary keys and include appropriate indexes for efficient
querying. The workflow_runs table has a foreign key relationship to workflow_definitions.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c5c726943b4d"
down_revision = "98b9b39fc6b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create workflow definition and execution tables.

    This function creates two new tables:
    1. workflow_definitions:
       - Stores workflow definitions with their steps and metadata
       - Uses UUID primary key
       - Includes name index for efficient lookups

    2. workflow_runs:
       - Stores workflow execution records
       - Uses UUID primary key
       - Has foreign key to workflow_definitions
       - Includes indexes for status and workflow_id
    """
    # Create workflow_definitions table
    op.create_table(
        "workflow_definitions",
        sa.Column("workflow_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("steps", sa.JSON(), nullable=False),
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
        sa.PrimaryKeyConstraint("workflow_id"),
    )
    op.create_index(
        op.f("ix_workflow_definitions_name"),
        "workflow_definitions",
        ["name"],
        unique=False,
    )

    # Create workflow_runs table
    op.create_table(
        "workflow_runs",
        sa.Column("run_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inputs", sa.JSON(), nullable=True),
        sa.Column("outputs", sa.JSON(), nullable=True),
        sa.Column("step_results", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflow_definitions.workflow_id"],
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        op.f("ix_workflow_runs_status"), "workflow_runs", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_workflow_runs_workflow_id"),
        "workflow_runs",
        ["workflow_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """
    Remove workflow definition and execution tables.

    This function drops the workflow_runs and workflow_definitions tables
    in the correct order to handle the foreign key dependency.
    """
    op.drop_index(op.f("ix_workflow_runs_workflow_id"), table_name="workflow_runs")
    op.drop_index(op.f("ix_workflow_runs_status"), table_name="workflow_runs")
    op.drop_table("workflow_runs")
    op.drop_index(
        op.f("ix_workflow_definitions_name"), table_name="workflow_definitions"
    )
    op.drop_table("workflow_definitions")
    # ### end Alembic commands ###
