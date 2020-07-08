""" Add `hidden` column to `Tasks`.

Revision ID: 27a835cae9b9
Revises: 2ea95f7d541c
Create Date: 2020-07-08 15:10:03.631769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27a835cae9b9'
down_revision = '2ea95f7d541c'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('tasks', sa.Column('hidden', sa.Boolean(), nullable=True))
    except Exception:
        pass

def downgrade():
    with op.batch_alter_table('tasks') as batch:
        batch.drop_column('hidden')
