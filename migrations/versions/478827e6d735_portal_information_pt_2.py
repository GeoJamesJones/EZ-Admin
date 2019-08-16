"""portal information, pt 2

Revision ID: 478827e6d735
Revises: b265b05da33d
Create Date: 2019-08-15 20:35:23.745094

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '478827e6d735'
down_revision = 'b265b05da33d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('portal_name', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_user_portal_name'), 'user', ['portal_name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_portal_name'), table_name='user')
    op.drop_column('user', 'portal_name')
    # ### end Alembic commands ###
