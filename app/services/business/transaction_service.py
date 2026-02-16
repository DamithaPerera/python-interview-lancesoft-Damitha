from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories import rate_repository, transaction_repository
from app.schemas import QuoteCreate, QuoteOut, TransactionCreate, TransactionOut
from app.services.business.calculators import get_calculator


def calculate_quote(db: Session, *, payload: QuoteCreate) -> QuoteOut | None:
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

    return QuoteOut(
        rate_date=payload.timestamp.date(),
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
