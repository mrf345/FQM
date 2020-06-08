""" Add `lp_printing` flag setting.

Revision ID: 9e5b998a4c7b
Revises: b41c62db00a1
Create Date: 2020-06-08 15:33:00.315047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e5b998a4c7b'
down_revision = 'b41c62db00a1'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('settings', sa.Column('lp_printing', sa.Boolean(), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('settings') as batch:
        batch.drop_column('lp_printing')
