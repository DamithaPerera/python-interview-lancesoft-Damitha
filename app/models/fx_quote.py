from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FxQuote(Base):
    __tablename__ = "fx_quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    quote_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    side: Mapped[str] = mapped_column(Enum("BUY", "SELL", name="quote_side"), nullable=False)

    foreign_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    effective_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=Decimal("0"))
    rounding_adjustment: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), nullable=False, default=Decimal("0")
    )

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
