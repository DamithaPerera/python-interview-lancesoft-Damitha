from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.schemas.transaction import TransactionCreate
from pydantic import BaseModel, ConfigDict


class QuoteCreate(TransactionCreate):
    pass


class QuoteOut(BaseModel):
    quote_id: str
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
    expires_at: datetime
    confirmed: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quote_id": "QTE-7f7ab84b03bf4d84a5f96dbe8db40d1f",
                "rate_date": "2026-02-16",
                "timestamp": "2026-02-16T09:19:34.939Z",
                "base_currency": "USD",
                "quote_currency": "PHP",
                "side": "BUY",
                "foreign_amount": "100.00",
                "base_amount": "5725.00",
                "effective_rate": "57.25000000",
                "fee_amount": "0",
                "rounding_adjustment": "0",
                "expires_at": "2026-02-16T09:34:34.939Z",
                "confirmed": False,
            }
        }
    )
