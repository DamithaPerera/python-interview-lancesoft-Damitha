from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import QUOTE_TTL_MINUTES
from app.repositories import quote_repository, rate_repository, transaction_repository
from app.schemas import (
    QuoteCreate,
    QuoteOut,
    TransactionConfirmCreate,
    TransactionCreate,
    TransactionOut,
)
from app.services.business.calculators import get_calculator


def create_quote(db: Session, *, payload: QuoteCreate) -> QuoteOut | None:
    rate = rate_repository.get_by_composite(
        db,
        rate_date=payload.timestamp.date(),
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
    )
    if not rate:
        return None

    calc = get_calculator(payload.side)
    result = calc.calculate(
        rate=rate.rate,
        foreign_amount=payload.foreign_amount,
        base_amount=payload.base_amount,
    )

    quote_id = f"QTE-{uuid4().hex}"
    now_utc = datetime.utcnow()
    expires_at = now_utc + timedelta(minutes=QUOTE_TTL_MINUTES)
    quote = quote_repository.create(
        db,
        quote_id=quote_id,
        quote_timestamp=payload.timestamp,
        rate_date=payload.timestamp.date(),
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
        foreign_amount=result.foreign_amount,
        base_amount=result.base_amount,
        effective_rate=result.effective_rate,
        fee_amount=result.fee_amount,
        rounding_adjustment=result.rounding_adjustment,
        expires_at=expires_at,
    )

    return QuoteOut(
        quote_id=quote.quote_id,
        rate_date=quote.rate_date,
        timestamp=quote.quote_timestamp,
        base_currency=quote.base_currency,
        quote_currency=quote.quote_currency,
        side=quote.side,
        foreign_amount=quote.foreign_amount,
        base_amount=quote.base_amount,
        effective_rate=quote.effective_rate,
        fee_amount=quote.fee_amount,
        rounding_adjustment=quote.rounding_adjustment,
        expires_at=quote.expires_at,
        confirmed=quote.confirmed,
    )


def create_transaction(db: Session, *, payload: TransactionCreate) -> TransactionOut | None:
    rate = rate_repository.get_by_composite(
        db,
        rate_date=payload.timestamp.date(),
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
    )
    if not rate:
        return None

    calc = get_calculator(payload.side)
    result = calc.calculate(
        rate=rate.rate,
        foreign_amount=payload.foreign_amount,
        base_amount=payload.base_amount,
    )

    txn = transaction_repository.create(
        db,
        timestamp=payload.timestamp,
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
        foreign_amount=result.foreign_amount,
        base_amount=result.base_amount,
        effective_rate=result.effective_rate,
        fee_amount=result.fee_amount,
        rounding_adjustment=result.rounding_adjustment,
    )

    return TransactionOut(
        transaction_id=txn.transaction_id,
        timestamp=txn.transaction_timestamp,
        base_currency=txn.base_currency,
        quote_currency=txn.quote_currency,
        side=txn.side,
        foreign_amount=txn.foreign_amount,
        base_amount=txn.base_amount,
        effective_rate=txn.effective_rate,
        fee_amount=txn.fee_amount,
        rounding_adjustment=txn.rounding_adjustment,
    )


def confirm_transaction(
    db: Session, *, payload: TransactionConfirmCreate
) -> TransactionOut | None | str:
    quote = quote_repository.get_by_quote_id(db, quote_id=payload.quote_id)
    if not quote:
        return "NOT_FOUND"
    if quote.confirmed:
        return "ALREADY_CONFIRMED"

    now_utc = datetime.utcnow()
    if quote.expires_at < now_utc:
        return "EXPIRED"

    txn = transaction_repository.create(
        db,
        timestamp=now_utc,
        base_currency=quote.base_currency,
        quote_currency=quote.quote_currency,
        side=quote.side,
        foreign_amount=quote.foreign_amount,
        base_amount=quote.base_amount,
        effective_rate=quote.effective_rate,
        fee_amount=quote.fee_amount,
        rounding_adjustment=quote.rounding_adjustment,
    )
    quote_repository.mark_confirmed(db, quote=quote, confirmed_at=now_utc)

    return TransactionOut(
        transaction_id=txn.transaction_id,
        timestamp=txn.transaction_timestamp,
        base_currency=txn.base_currency,
        quote_currency=txn.quote_currency,
        side=txn.side,
        foreign_amount=txn.foreign_amount,
        base_amount=txn.base_amount,
        effective_rate=txn.effective_rate,
        fee_amount=txn.fee_amount,
        rounding_adjustment=txn.rounding_adjustment,
    )
