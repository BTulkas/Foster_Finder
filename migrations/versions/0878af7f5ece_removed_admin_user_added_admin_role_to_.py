"""Removed admin user. Added admin role to clinic

Revision ID: 0878af7f5ece
Revises: 4a1d6288f3f5
Create Date: 2020-08-31 12:11:57.939066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0878af7f5ece'
down_revision = '4a1d6288f3f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clinic', sa.Column('admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clinic', 'admin')
    # ### end Alembic commands ###