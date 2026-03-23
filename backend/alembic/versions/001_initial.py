"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2025-03-21

"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("bonus_balance", sa.Numeric(10, 2), server_default=sa.text("0")),
        sa.Column("referrer_id", sa.Integer(), nullable=True),
        sa.Column("total_spent", sa.Numeric(12, 2), server_default=sa.text("0")),
        sa.Column("visit_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("tags", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["referrer_id"], ["users.id"]),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # Service Categories
    op.create_table(
        "service_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("icon", sa.String(10), nullable=False, server_default="🔧"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Services
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_min_hours", sa.Numeric(5, 2), server_default=sa.text("1.0")),
        sa.Column("duration_max_hours", sa.Numeric(5, 2), server_default=sa.text("2.0")),
        sa.Column("has_car_classes", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("is_package", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["category_id"], ["service_categories.id"]),
    )

    # Service Prices
    op.create_table(
        "service_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("car_class", sa.String(10), nullable=True),
        sa.Column("package_name", sa.String(50), nullable=True),
        sa.Column("price_from", sa.Numeric(10, 2), nullable=False),
        sa.Column("price_to", sa.Numeric(10, 2), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
    )

    # Work Posts
    op.create_table(
        "work_posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("specialization", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Blocked Slots
    op.create_table(
        "blocked_slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_start", sa.Time(), nullable=False),
        sa.Column("time_end", sa.Time(), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["post_id"], ["work_posts.id"]),
    )

    # Bookings
    booking_status = sa.Enum("new", "confirmed", "in_progress", "completed", "cancelled", "no_show", name="bookingstatus")
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=True),
        sa.Column("car_brand", sa.String(100), nullable=False, server_default=""),
        sa.Column("car_model", sa.String(100), nullable=False, server_default=""),
        sa.Column("car_class", sa.String(10), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_start", sa.Time(), nullable=False),
        sa.Column("time_end", sa.Time(), nullable=False),
        sa.Column("status", booking_status, server_default="new"),
        sa.Column("price_estimated", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_final", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("bonus_used", sa.Numeric(10, 2), server_default=sa.text("0")),
        sa.Column("bonus_earned", sa.Numeric(10, 2), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("reminder_24h_sent", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("reminder_2h_sent", sa.Boolean(), server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.ForeignKeyConstraint(["post_id"], ["work_posts.id"]),
    )

    # Portfolio Items
    op.create_table(
        "portfolio_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("service_id", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("image_before_url", sa.String(500), nullable=True),
        sa.Column("car_brand", sa.String(100), nullable=True),
        sa.Column("car_model", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instagram_url", sa.String(500), nullable=True),
        sa.Column("is_visible", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["category_id"], ["service_categories.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
    )

    # Bonus Transactions
    bonus_type = sa.Enum("cashback", "referral_bonus", "referral_welcome", "spent", "expired", name="bonustype")
    op.create_table(
        "bonus_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("type", bonus_type, nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
    )

    # Promotions
    discount_type = sa.Enum("percent", "fixed", "gift", name="discounttype")
    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("discount_type", discount_type, nullable=False),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("date_start", sa.Date(), nullable=False),
        sa.Column("date_end", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Promotion Services (M2M)
    op.create_table(
        "promotion_services",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("promotion_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["promotion_id"], ["promotions.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
    )

    # FAQ
    op.create_table(
        "faqs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.String(255), nullable=False),
        sa.Column("question", sa.String(1000), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    # Broadcasts
    broadcast_segment = sa.Enum("all", "recent", "inactive", "by_service", "vip", name="broadcastsegment")
    broadcast_status = sa.Enum("draft", "scheduled", "sending", "sent", name="broadcaststatus")
    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("buttons", sa.JSON(), nullable=True),
        sa.Column("segment", broadcast_segment, server_default="all"),
        sa.Column("segment_params", sa.JSON(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_sent", sa.Integer(), server_default=sa.text("0")),
        sa.Column("total_errors", sa.Integer(), server_default=sa.text("0")),
        sa.Column("status", broadcast_status, server_default="draft"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("broadcasts")
    op.drop_table("faqs")
    op.drop_table("promotion_services")
    op.drop_table("promotions")
    op.drop_table("bonus_transactions")
    op.drop_table("portfolio_items")
    op.drop_table("bookings")
    op.drop_table("blocked_slots")
    op.drop_table("work_posts")
    op.drop_table("service_prices")
    op.drop_table("services")
    op.drop_table("service_categories")
    op.drop_table("users")

    sa.Enum(name="bookingstatus").drop(op.get_bind())
    sa.Enum(name="bonustype").drop(op.get_bind())
    sa.Enum(name="discounttype").drop(op.get_bind())
    sa.Enum(name="broadcastsegment").drop(op.get_bind())
    sa.Enum(name="broadcaststatus").drop(op.get_bind())
