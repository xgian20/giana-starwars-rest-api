"""empty message

Revision ID: 8d5e0d82a81d
Revises: 99e733493fe3
Create Date: 2024-08-28 13:20:59.229644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d5e0d82a81d'
down_revision = '99e733493fe3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorite_people', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_person_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'person', ['favorite_person_id'], ['id'])

    with op.batch_alter_table('favorite_planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_planet_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'planet', ['favorite_planet_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorite_planets', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('favorite_planet_id')

    with op.batch_alter_table('favorite_people', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('favorite_person_id')

    # ### end Alembic commands ###
