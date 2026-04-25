"""add unique constraints to likes and matches

Revision ID: c9f2e1a4b3d7
Revises: 8d3a2b7f4c1e
Create Date: 2026-04-26 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'c9f2e1a4b3d7'
down_revision: Union[str, None] = '8d3a2b7f4c1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('likes', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_like_from_to', ['from_user_id', 'to_user_id'])

    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_match_users', ['user1_id', 'user2_id'])


def downgrade() -> None:
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_constraint('uq_match_users', type_='unique')

    with op.batch_alter_table('likes', schema=None) as batch_op:
        batch_op.drop_constraint('uq_like_from_to', type_='unique')
