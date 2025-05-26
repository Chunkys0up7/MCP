"""Add users table

Revision ID: 999999999999
Revises: 8f318fe1d021
Create Date: 2024-05-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '999999999999'
down_revision = '8f318fe1d021'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('username', sa.String(length=64), unique=True, nullable=False),
        sa.Column('email', sa.String(length=128), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(length=256), nullable=False),
        sa.Column('roles', sa.String(length=128), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

def downgrade():
    op.drop_table('users') 