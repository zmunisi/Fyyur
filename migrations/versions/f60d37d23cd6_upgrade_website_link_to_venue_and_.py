"""Upgrade website_link to Venue and Artist Model

Revision ID: f60d37d23cd6
Revises: f65f11d02f5b
Create Date: 2021-04-09 09:24:47.341950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f60d37d23cd6'
down_revision = 'f65f11d02f5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('artists', 'website')
    op.add_column('venues', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('venues', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('venues', 'website_link')
    op.add_column('artists', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('artists', 'website_link')
    # ### end Alembic commands ###
