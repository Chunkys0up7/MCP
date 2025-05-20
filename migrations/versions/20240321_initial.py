"""Initial migration

Revision ID: 20240321_initial
Revises: 
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240321_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create mcp_configurations table
    op.create_table(
        'mcp_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('dependencies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_modified', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("type IN ('llm', 'tool', 'chain')", name='valid_type_check')
    )

    # Create mcp_chains table
    op.create_table(
        'mcp_chains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('workflow', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('parent_chain', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_chain'], ['mcp_chains.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chain_sessions table
    op.create_table(
        'chain_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('chain_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

    # Create mcp_permissions table
    op.create_table(
        'mcp_permissions',
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('chain_id', sa.Integer(), nullable=False),
        sa.Column('access_level', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['chain_id'], ['mcp_chains.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'chain_id'),
        sa.CheckConstraint("access_level IN ('read', 'write', 'admin')", name='valid_access_level_check')
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('mcp_permissions')
    op.drop_table('chain_sessions')
    op.drop_table('mcp_chains')
    op.drop_table('mcp_configurations') 