""" Adding `wait_for_announcement` default option to display.

Revision ID: 8e8e57b30162
Revises: 9e5b998a4c7b
Create Date: 2020-06-15 07:21:17.661614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e8e57b30162'
down_revision = '9e5b998a4c7b'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('displays', sa.Column('wait_for_announcement', sa.Boolean(), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('displays') as batch:
        batch.drop_column('wait_for_announcement')
