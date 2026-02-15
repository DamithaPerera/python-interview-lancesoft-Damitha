from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FxTransaction(Base):
    __tablename__ = "fx_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[str | None] = mapped_column(String(32), unique=True)
    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    side: Mapped[str] = mapped_column(Enum("BUY", "SELL", name="txn_side"), nullable=False)

    foreign_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=True)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=True)

    effective_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=Decimal("0"))
    rounding_adjustment: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), nullable=False, default=Decimal("0")
    )
