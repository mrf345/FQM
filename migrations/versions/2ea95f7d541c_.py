""" Add `single_row` flag setting.

Revision ID: 2ea95f7d541c
Revises: 8e8e57b30162
Create Date: 2020-06-16 18:17:55.745006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ea95f7d541c'
down_revision = '8e8e57b30162'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('settings', sa.Column('single_row', sa.Boolean(), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('settings') as batch:
        batch.drop_column('single_row')
