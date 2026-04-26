"""initial

Revision ID: 3b8e04439b2f
Revises: 
Create Date: 2026-04-25 21:32:37.985244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b8e04439b2f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("password_hash", sa.String(), nullable=False),
            sa.Column("full_name", sa.String(), nullable=False),
            sa.Column("age", sa.Integer(), nullable=True),
            sa.Column("city", sa.String(), nullable=True),
            sa.Column("bio", sa.Text(), nullable=True),
            sa.Column("photo_url", sa.String(), nullable=True),
            sa.Column("role", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("interests", sa.Text(), nullable=True),
            sa.Column("travel_style", sa.String(), nullable=True),
            sa.Column("budget_min", sa.Float(), nullable=True),
            sa.Column("budget_max", sa.Float(), nullable=True),
            sa.Column("languages", sa.Text(), nullable=True),
            sa.Column("complaint_count", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    if not inspector.has_table("partners"):
        op.create_table(
            "partners",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("company_name", sa.String(), nullable=False),
            sa.Column("legal_info", sa.Text(), nullable=True),
            sa.Column("partner_type", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("commission_rate", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_partners_id"), "partners", ["id"], unique=False)

    if not inspector.has_table("packages"):
        op.create_table(
            "packages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("partner_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("destination", sa.String(), nullable=False),
            sa.Column("region", sa.String(), nullable=True),
            sa.Column("price", sa.Float(), nullable=False),
            sa.Column("duration_days", sa.Integer(), nullable=False),
            sa.Column("min_group_size", sa.Integer(), nullable=True),
            sa.Column("max_group_size", sa.Integer(), nullable=True),
            sa.Column("inclusions", sa.Text(), nullable=True),
            sa.Column("exclusions", sa.Text(), nullable=True),
            sa.Column("cancellation_policy", sa.Text(), nullable=True),
            sa.Column("itinerary", sa.Text(), nullable=True),
            sa.Column("photo_url", sa.String(), nullable=True),
            sa.Column("difficulty", sa.String(), nullable=True),
            sa.Column("travel_style", sa.String(), nullable=True),
            sa.Column("family_friendly", sa.Boolean(), nullable=True),
            sa.Column("family_rates_enabled", sa.Boolean(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("featured", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["partner_id"], ["partners.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_packages_id"), "packages", ["id"], unique=False)

    if not inspector.has_table("package_dates"):
        op.create_table(
            "package_dates",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("package_id", sa.Integer(), nullable=True),
            sa.Column("start_date", sa.DateTime(), nullable=False),
            sa.Column("total_slots", sa.Integer(), nullable=False),
            sa.Column("available_slots", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(["package_id"], ["packages.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_package_dates_id"), "package_dates", ["id"], unique=False)

    if not inspector.has_table("bookings"):
        op.create_table(
            "bookings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("package_id", sa.Integer(), nullable=True),
            sa.Column("package_date_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("num_travelers", sa.Integer(), nullable=True),
            sa.Column("is_family_booking", sa.Boolean(), nullable=True),
            sa.Column("family_discount_pct", sa.Float(), nullable=True),
            sa.Column("base_price", sa.Float(), nullable=False),
            sa.Column("total_price", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("paid_at", sa.DateTime(), nullable=True),
            sa.Column("confirmed_at", sa.DateTime(), nullable=True),
            sa.Column("cancellation_reason", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(["package_date_id"], ["package_dates.id"]),
            sa.ForeignKeyConstraint(["package_id"], ["packages.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)

    if not inspector.has_table("waiting_list"):
        op.create_table(
            "waiting_list",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("package_date_id", sa.Integer(), nullable=True),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("offer_expires_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.ForeignKeyConstraint(["package_date_id"], ["package_dates.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_waiting_list_id"), "waiting_list", ["id"], unique=False)

    if not inspector.has_table("trips"):
        op.create_table(
            "trips",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("organizer_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("destination", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("start_date", sa.DateTime(), nullable=False),
            sa.Column("end_date", sa.DateTime(), nullable=False),
            sa.Column("min_size", sa.Integer(), nullable=True),
            sa.Column("max_size", sa.Integer(), nullable=True),
            sa.Column("current_size", sa.Integer(), nullable=True),
            sa.Column("budget_min", sa.Float(), nullable=True),
            sa.Column("budget_max", sa.Float(), nullable=True),
            sa.Column("travel_style", sa.String(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("photo_url", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["organizer_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_trips_id"), "trips", ["id"], unique=False)

    if not inspector.has_table("trip_members"):
        op.create_table(
            "trip_members",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("trip_id", sa.Integer(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("joined_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["trip_id"], ["trips.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_trip_members_id"), "trip_members", ["id"], unique=False)

    if not inspector.has_table("likes"):
        op.create_table(
            "likes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("from_user_id", sa.Integer(), nullable=True),
            sa.Column("to_user_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["from_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["to_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_likes_id"), "likes", ["id"], unique=False)

    if not inspector.has_table("matches"):
        op.create_table(
            "matches",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user1_id", sa.Integer(), nullable=True),
            sa.Column("user2_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user1_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["user2_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_matches_id"), "matches", ["id"], unique=False)

    if not inspector.has_table("messages"):
        op.create_table(
            "messages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("match_id", sa.Integer(), nullable=True),
            sa.Column("sender_id", sa.Integer(), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
            sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)

    if not inspector.has_table("reviews"):
        op.create_table(
            "reviews",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("package_id", sa.Integer(), nullable=True),
            sa.Column("booking_id", sa.Integer(), nullable=True),
            sa.Column("rating", sa.Float(), nullable=False),
            sa.Column("text", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
            sa.ForeignKeyConstraint(["package_id"], ["packages.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("booking_id"),
        )
        op.create_index(op.f("ix_reviews_id"), "reviews", ["id"], unique=False)

    if not inspector.has_table("complaints"):
        op.create_table(
            "complaints",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("reporter_id", sa.Integer(), nullable=True),
            sa.Column("target_user_id", sa.Integer(), nullable=True),
            sa.Column("reason", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["reporter_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["target_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_complaints_id"), "complaints", ["id"], unique=False)


def downgrade() -> None:
    for table_name in (
        "complaints",
        "reviews",
        "messages",
        "matches",
        "likes",
        "trip_members",
        "trips",
        "waiting_list",
        "bookings",
        "package_dates",
        "packages",
        "partners",
        "users",
    ):
        op.drop_table(table_name)
