from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class TransactionCreate(BaseModel):
    timestamp: datetime
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    side: str
    foreign_amount: Decimal | None = None
    base_amount: Decimal | None = None

    @field_validator("base_currency", "quote_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v = v.upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a 3-letter ISO code")
        return v

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        v = v.upper()
        if v not in {"BUY", "SELL"}:
            raise ValueError("Side must be BUY or SELL")
        return v

    @field_validator("foreign_amount", "base_amount")
    @classmethod
    def validate_amount(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @model_validator(mode="after")
    def validate_exclusive(self):
        if (self.foreign_amount is None and self.base_amount is None) or (
            self.foreign_amount is not None and self.base_amount is not None
        ):
            raise ValueError("Provide exactly one of foreign_amount or base_amount")
        return self


class TransactionOut(BaseModel):
    transaction_id: str
    timestamp: datetime
    base_currency: str
    quote_currency: str
    side: str
    foreign_amount: Decimal
    base_amount: Decimal
    effective_rate: Decimal
    fee_amount: Decimal
    rounding_adjustment: Decimal

    class Config:
        from_attributes = True
