"""individual matching: user_skips table + contact columns on users

Revision ID: d4f1e2b3c8a9
Revises: c9f2e1a4b3d7
Create Date: 2026-04-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'd4f1e2b3c8a9'
down_revision = 'c9f2e1a4b3d7'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()

    # create_all may have already created user_skips on dev startup — skip if so
    if 'user_skips' not in existing_tables:
        op.create_table(
            'user_skips',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('from_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('to_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('from_user_id', 'to_user_id', name='uq_skip_from_to'),
        )
        op.create_index('ix_user_skips_id', 'user_skips', ['id'], unique=False)

    existing_columns = {col['name'] for col in inspector.get_columns('users')}
    new_cols = [
        ('phone',     sa.String()),
        ('telegram',  sa.String()),
        ('whatsapp',  sa.String()),
        ('instagram', sa.String()),
    ]
    with op.batch_alter_table('users') as batch_op:
        for col_name, col_type in new_cols:
            if col_name not in existing_columns:
                batch_op.add_column(sa.Column(col_name, col_type, nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        for col_name in ('instagram', 'whatsapp', 'telegram', 'phone'):
            batch_op.drop_column(col_name)

    op.drop_index('ix_user_skips_id', table_name='user_skips')
    op.drop_table('user_skips')
