"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-17 00:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


rate_side_enum = sa.Enum("BUY", "SELL", name="rate_side")
quote_side_enum = sa.Enum("BUY", "SELL", name="quote_side")
txn_side_enum = sa.Enum("BUY", "SELL", name="txn_side")


def upgrade() -> None:
    op.create_table(
        "daily_rates",
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("side", rate_side_enum, nullable=False),
        sa.Column("rate", sa.Numeric(18, 8), nullable=False),
        sa.PrimaryKeyConstraint(
            "rate_date", "base_currency", "quote_currency", "side", name="pk_daily_rate"
        ),
    )

    op.create_table(
        "fx_quotes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quote_id", sa.String(length=64), nullable=False),
        sa.Column("quote_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rate_date", sa.Date(), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("side", quote_side_enum, nullable=False),
        sa.Column("foreign_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("base_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("effective_rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("fee_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("rounding_adjustment", sa.Numeric(18, 6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quote_id"),
    )

    op.create_table(
        "fx_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(length=32), nullable=True),
        sa.Column("transaction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("side", txn_side_enum, nullable=False),
        sa.Column("foreign_amount", sa.Numeric(18, 6), nullable=True),
        sa.Column("base_amount", sa.Numeric(18, 6), nullable=True),
        sa.Column("effective_rate", sa.Numeric(18, 8), nullable=False),
        sa.Column("fee_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("rounding_adjustment", sa.Numeric(18, 6), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )


def downgrade() -> None:
    op.drop_table("fx_transactions")
    op.drop_table("fx_quotes")
    op.drop_table("daily_rates")
