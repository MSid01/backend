"""Dummy table

Revision ID: a4029135a0f8
Revises: 
Create Date: 2022-08-31 14:16:05.192336

"""
from operator import index

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4029135a0f8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dumb', sa.Column('bump', sa.Integer(), index=True))
    # ### end Alembic commands ###

