"""Add missing fields to Venue and Artist

Revision ID: 6292f502ca9e
Revises: 0acb151fd6ff
Create Date: 2021-04-02 16:26:11.733111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6292f502ca9e'
down_revision = '0acb151fd6ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.alter_column('Artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('Artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.alter_column('Venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('Venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'genres')
    op.alter_column('Artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('Artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_talent')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
