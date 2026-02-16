from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyRate(Base):
    __tablename__ = "daily_rates"
    __table_args__ = (
        PrimaryKeyConstraint(
            "rate_date", "base_currency", "quote_currency", "side", name="pk_daily_rate"
        ),
    )

    rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    side: Mapped[str] = mapped_column(Enum("BUY", "SELL", name="rate_side"), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
