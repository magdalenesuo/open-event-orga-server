"""empty message

Revision ID: 4525c3f044c3
Revises: d469443aed74
Create Date: 2016-08-08 18:39:16.343588

"""

# revision identifiers, used by Alembic.
revision = '4525c3f044c3'
down_revision = 'd469443aed74'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ticket_fees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(), nullable=True),
    sa.Column('service_fee', sa.Float(), nullable=True),
    sa.Column('maximum_fee', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column(u'events', 'event_url')
    op.drop_column(u'events_version', 'event_url')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'events_version', sa.Column('event_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(u'events', sa.Column('event_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_table('ticket_fees')
    ### end Alembic commands ###