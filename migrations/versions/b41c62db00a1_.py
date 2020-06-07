""" Convert printer `vendor` and `product` to int type. And add `name`. 

Revision ID: b41c62db00a1
Revises: d37b1524c3fc
Create Date: 2020-06-06 16:49:00.859545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b41c62db00a1'
down_revision = 'd37b1524c3fc'
branch_labels = None
depends_on = None


def upgrade():
    try:
        with op.batch_alter_table('printers') as batch:
            batch.alter_column('vendor',
                               existing_type=sa.VARCHAR(length=100),
                               type_=sa.Integer(),
                               existing_nullable=True)
            batch.alter_column('product',
                               existing_type=sa.VARCHAR(length=100),
                               type_=sa.Integer(),
                               existing_nullable=True)
            batch.add_column(sa.Column('name', sa.String(100), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('printers') as batch:
        batch.alter_column('vendor',
                           existing_type=sa.Integer(),
                           type_=sa.VARCHAR(length=100),
                           existing_nullable=True)
        batch.alter_column('product',
                           existing_type=sa.Integer(),
                           type_=sa.VARCHAR(length=100),
                           existing_nullable=True)
        batch.drop_column('name')
