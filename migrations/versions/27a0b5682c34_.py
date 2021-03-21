"""Add header and sub-header fields to Printer

Revision ID: 27a0b5682c34
Revises: cf6ed76ef146
Create Date: 2021-03-21 17:33:20.771426

"""
from alembic import op
import sqlalchemy as sa


revision = '27a0b5682c34'
down_revision = 'cf6ed76ef146'
branch_labels = None
depends_on = None


def upgrade():
    try:
        op.add_column('printers', sa.Column('header', sa.String(length=50), nullable=True))
        op.add_column('printers', sa.Column('sub', sa.String(length=100), nullable=True))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('printers') as b:
        b.drop_column('sub')
        b.drop_column('header')
