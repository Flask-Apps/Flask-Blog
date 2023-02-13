"""empty message

Revision ID: d36018831649
Revises: 661974054f3d
Create Date: 2023-02-13 09:18:06.873624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd36018831649'
down_revision = '661974054f3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('member_since', sa.DateTime(), nullable=True))
        batch_op.drop_column('memeber_since')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('memeber_since', sa.DATETIME(), nullable=True))
        batch_op.drop_column('member_since')

    # ### end Alembic commands ###
