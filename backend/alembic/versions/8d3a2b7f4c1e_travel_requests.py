"""travel requests and partner offers

Revision ID: 8d3a2b7f4c1e
Revises: 3b8e04439b2f
Create Date: 2026-04-25 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "8d3a2b7f4c1e"
down_revision: Union[str, None] = "3b8e04439b2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())

    if not inspector.has_table("travel_requests"):
        op.create_table(
            "travel_requests",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("origin", sa.String(), nullable=False),
            sa.Column("days", sa.String(), nullable=False),
            sa.Column("companions", sa.String(), nullable=False),
            sa.Column("interests", sa.Text(), nullable=True),
            sa.Column("travel_format", sa.String(), nullable=False),
            sa.Column("mood", sa.String(), nullable=True),
            sa.Column("difficulty", sa.String(), nullable=False),
            sa.Column("budget", sa.String(), nullable=False),
            sa.Column("season", sa.String(), nullable=False),
            sa.Column("accommodation", sa.String(), nullable=True),
            sa.Column("transport", sa.String(), nullable=True),
            sa.Column("activities", sa.Text(), nullable=True),
            sa.Column("preferred_places", sa.Text(), nullable=True),
            sa.Column("distance", sa.String(), nullable=True),
            sa.Column("priority", sa.String(), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_travel_requests_id"), "travel_requests", ["id"], unique=False)
        op.create_index(op.f("ix_travel_requests_user_id"), "travel_requests", ["user_id"], unique=False)

    if not inspector.has_table("travel_offers"):
        op.create_table(
            "travel_offers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("request_id", sa.Integer(), nullable=False),
            sa.Column("partner_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price_total", sa.Float(), nullable=False),
            sa.Column("price_per_person", sa.Float(), nullable=True),
            sa.Column("duration_days", sa.Integer(), nullable=True),
            sa.Column("included", sa.Text(), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["partner_id"], ["partners.id"]),
            sa.ForeignKeyConstraint(["request_id"], ["travel_requests.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_travel_offers_id"), "travel_offers", ["id"], unique=False)
        op.create_index(op.f("ix_travel_offers_partner_id"), "travel_offers", ["partner_id"], unique=False)
        op.create_index(op.f("ix_travel_offers_request_id"), "travel_offers", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_travel_offers_request_id"), table_name="travel_offers")
    op.drop_index(op.f("ix_travel_offers_partner_id"), table_name="travel_offers")
    op.drop_index(op.f("ix_travel_offers_id"), table_name="travel_offers")
    op.drop_table("travel_offers")
    op.drop_index(op.f("ix_travel_requests_user_id"), table_name="travel_requests")
    op.drop_index(op.f("ix_travel_requests_id"), table_name="travel_requests")
    op.drop_table("travel_requests")
