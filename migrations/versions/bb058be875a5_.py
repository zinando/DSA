"""empty message

Revision ID: bb058be875a5
Revises: 19e8eddba358
Create Date: 2023-07-24 17:40:27.693243

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb058be875a5'
down_revision = '19e8eddba358'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stepup_cards',
    sa.Column('sucid', sa.Integer(), nullable=False),
    sa.Column('training_id', sa.String(length=250), nullable=False),
    sa.Column('last_review', sa.DateTime(), nullable=True),
    sa.Column('suc_link', sa.String(length=650), nullable=True),
    sa.PrimaryKeyConstraint('sucid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stepup_cards')
    # ### end Alembic commands ###