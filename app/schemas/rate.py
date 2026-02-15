from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class RateBase(BaseModel):
    rate_date: date
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    side: str
    rate: Decimal

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

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Rate must be positive")
        return v


class RateCreate(RateBase):
    pass


class RateUpdate(BaseModel):
    rate: Decimal

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Rate must be positive")
        return v


class RateOut(RateBase):
    id: int

    class Config:
        from_attributes = True
