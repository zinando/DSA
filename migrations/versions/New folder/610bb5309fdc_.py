"""empty message

Revision ID: 610bb5309fdc
Revises: b4fb3ef0abb6
Create Date: 2022-08-28 11:24:38.201072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '610bb5309fdc'
down_revision = 'b4fb3ef0abb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('production', sa.Column('exp_msu', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('production', 'exp_msu')
    # ### end Alembic commands ###