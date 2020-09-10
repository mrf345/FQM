"""Add `AuthTokens` table.

Revision ID: cf6ed76ef146
Revises: 8da7405903f6
Create Date: 2020-09-10 17:13:40.407017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf6ed76ef146'
down_revision = '8da7405903f6'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.create_table(
            'auth_tokens',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=True),
            sa.Column('description', sa.String(length=300), nullable=True),
            sa.Column('token', sa.String(length=32), nullable=True),
            sa.Column('role_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('token'))
    except Exception:
        pass


def downgrade():
    op.drop_table('auth_tokens')
