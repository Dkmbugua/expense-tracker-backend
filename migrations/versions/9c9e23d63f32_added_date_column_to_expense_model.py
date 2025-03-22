"""Added date column to Expense model

Revision ID: 9c9e23d63f32
Revises: d78f2711708a
Create Date: 2025-03-21 15:25:56.514685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c9e23d63f32'
down_revision = 'd78f2711708a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DateTime(), nullable=False, server_default=sa.func.now()))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_column('date')

    # ### end Alembic commands ###
