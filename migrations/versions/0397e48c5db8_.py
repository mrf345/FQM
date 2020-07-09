""" Alter `offices.name` from integer to string.

Revision ID: 0397e48c5db8
Revises: 27a835cae9b9
Create Date: 2020-07-09 16:36:32.059383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0397e48c5db8'
down_revision = '27a835cae9b9'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.alter_column('offices',
                        'name',
                        existing_type=sa.INTEGER(),
                        type_=sa.String(length=300),
                        existing_nullable=False)
    except Exception:
        pass

def downgrade():
    with op.batch_alter_table('offices') as batch:
        batch.alter_column('offices',
                           'name',
                           existing_type=sa.String(length=300),
                           type_=sa.INTEGER(),
                           existing_nullable=False)
