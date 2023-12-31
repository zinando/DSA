"""empty message

Revision ID: 041b08d884d9
Revises: 0a9397faa000
Create Date: 2022-07-31 11:40:47.494247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '041b08d884d9'
down_revision = '0a9397faa000'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ogc_bos',
    sa.Column('ogcid', sa.Integer(), nullable=False),
    sa.Column('userid', sa.BigInteger(), nullable=False),
    sa.Column('observer', sa.String(length=60), nullable=False),
    sa.Column('department', sa.BigInteger(), nullable=False),
    sa.Column('line', sa.String(length=50), nullable=False),
    sa.Column('shift', sa.String(length=50), nullable=False),
    sa.Column('bos_type', sa.String(length=50), nullable=False),
    sa.Column('team', sa.String(length=50), nullable=True),
    sa.Column('bos_time', sa.DateTime(), nullable=False),
    sa.Column('percent', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('observation', sa.String(length=650), nullable=True),
    sa.Column('outages', sa.String(length=650), nullable=True),
    sa.Column('comment', sa.String(length=265), nullable=True),
    sa.Column('action', sa.String(length=265), nullable=True),
    sa.Column('regdate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('ogcid')
    )
    op.create_table('qa_bos',
    sa.Column('qid', sa.Integer(), nullable=False),
    sa.Column('userid', sa.BigInteger(), nullable=False),
    sa.Column('observer', sa.String(length=60), nullable=False),
    sa.Column('department', sa.BigInteger(), nullable=False),
    sa.Column('line', sa.String(length=50), nullable=False),
    sa.Column('shift', sa.String(length=50), nullable=False),
    sa.Column('bos_type', sa.String(length=50), nullable=False),
    sa.Column('team', sa.String(length=50), nullable=True),
    sa.Column('bos_time', sa.DateTime(), nullable=False),
    sa.Column('percent', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('observation', sa.String(length=650), nullable=True),
    sa.Column('outages', sa.String(length=650), nullable=True),
    sa.Column('comment', sa.String(length=265), nullable=True),
    sa.Column('action', sa.String(length=265), nullable=True),
    sa.Column('regdate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('qid')
    )
    op.create_table('safety_bos',
    sa.Column('sid', sa.Integer(), nullable=False),
    sa.Column('userid', sa.BigInteger(), nullable=False),
    sa.Column('observer', sa.String(length=60), nullable=False),
    sa.Column('department', sa.BigInteger(), nullable=False),
    sa.Column('line', sa.String(length=50), nullable=False),
    sa.Column('shift', sa.String(length=50), nullable=False),
    sa.Column('bos_type', sa.String(length=50), nullable=False),
    sa.Column('team', sa.String(length=50), nullable=True),
    sa.Column('bos_time', sa.DateTime(), nullable=False),
    sa.Column('percent', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('observation', sa.String(length=650), nullable=True),
    sa.Column('outages', sa.String(length=650), nullable=True),
    sa.Column('comment', sa.String(length=265), nullable=True),
    sa.Column('action', sa.String(length=265), nullable=True),
    sa.Column('regdate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('sid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('safety_bos')
    op.drop_table('qa_bos')
    op.drop_table('ogc_bos')
    # ### end Alembic commands ###
