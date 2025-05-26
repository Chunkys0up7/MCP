"""Convert mcps.type to PostgreSQL enum

Revision ID: 999999999998
Revises: 999999999999
Create Date: 2024-05-27

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '999999999998'
down_revision = '999999999999'
branch_labels = None
depends_on = None

def upgrade():
    # Create the new enum type
    mcptype_enum = sa.Enum('llm_prompt', 'jupyter_notebook', 'python_script', 'ai_assistant', name='mcptype')
    mcptype_enum.create(op.get_bind(), checkfirst=True)
    # Alter the column to use the new enum type
    op.alter_column('mcps', 'type', type_=mcptype_enum, existing_type=sa.String(length=50), postgresql_using='type::mcptype')

def downgrade():
    # Convert back to string
    op.alter_column('mcps', 'type', type_=sa.String(length=50), existing_type=sa.Enum('llm_prompt', 'jupyter_notebook', 'python_script', 'ai_assistant', name='mcptype'), postgresql_using='type::text')
    # Drop the enum type
    op.execute('DROP TYPE mcptype') 