"""Add BackgroundTasks settings table.

Revision ID: 8da7405903f6
Revises: 69efa7247067
Create Date: 2020-09-05 20:02:53.642956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8da7405903f6'
down_revision = '69efa7247067'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.create_table(
            'background_tasks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=True),
            sa.Column('enabled', sa.Boolean(), nullable=True),
            sa.Column('every', sa.String(length=10), nullable=True),
            sa.Column('time', sa.Time(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'))
    except Exception:
        pass


def downgrade():
    op.drop_table('background_tasks')
