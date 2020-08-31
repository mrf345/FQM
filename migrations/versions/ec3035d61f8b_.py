"""Add status column to tickets.

Revision ID: ec3035d61f8b
Revises: 0397e48c5db8
Create Date: 2020-08-30 21:04:30.936267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec3035d61f8b'
down_revision = '0397e48c5db8'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('serials', sa.Column('status', sa.String(length=10), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('serials') as batch:
        batch.drop_column('status')
