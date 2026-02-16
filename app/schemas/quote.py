from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.schemas.transaction import TransactionCreate
from pydantic import BaseModel


class QuoteCreate(TransactionCreate):
    pass


class QuoteOut(BaseModel):
    rate_date: date
    timestamp: datetime
    base_currency: str
    quote_currency: str
    side: str
    foreign_amount: Decimal
    base_amount: Decimal
    effective_rate: Decimal
    fee_amount: Decimal
    rounding_adjustment: Decimal
