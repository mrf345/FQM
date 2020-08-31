"""Add hide_ticket_index option to Display Customization.

Revision ID: 69efa7247067
Revises: ec3035d61f8b
Create Date: 2020-08-31 22:05:00.672787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69efa7247067'
down_revision = 'ec3035d61f8b'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('displays', sa.Column('hide_ticket_index', sa.Boolean(), nullable=True))
    except Exception:
        pass

def downgrade():
    with op.batch_alter_table('displays') as batch:
        batch.drop_column('hide_ticket_index')
