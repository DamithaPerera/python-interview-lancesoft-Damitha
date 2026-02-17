from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FxQuote


def create(
    db: Session,
    *,
    quote_id: str,
    quote_timestamp: datetime,
    rate_date,
    base_currency: str,
    quote_currency: str,
    side: str,
    foreign_amount: Decimal,
    base_amount: Decimal,
    effective_rate: Decimal,
    fee_amount: Decimal,
    rounding_adjustment: Decimal,
    expires_at: datetime,
) -> FxQuote:
    quote = FxQuote(
        quote_id=quote_id,
        quote_timestamp=quote_timestamp,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
        foreign_amount=foreign_amount,
        base_amount=base_amount,
        effective_rate=effective_rate,
        fee_amount=fee_amount,
        rounding_adjustment=rounding_adjustment,
        expires_at=expires_at,
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def get_by_quote_id(db: Session, *, quote_id: str) -> FxQuote | None:
    stmt = select(FxQuote).where(FxQuote.quote_id == quote_id)
    return db.execute(stmt).scalar_one_or_none()


def mark_confirmed(db: Session, *, quote: FxQuote, confirmed_at: datetime) -> FxQuote:
    quote.confirmed = True
    quote.confirmed_at = confirmed_at
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote
