from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import DailyRate
from app.repositories import rate_repository


def create_or_update_rate(
    db: Session,
    *,
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
    rate: Decimal,
) -> DailyRate:
    return rate_repository.upsert(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
        rate=rate,
    )


def get_rates(
    db: Session,
    *,
    rate_date: date | None = None,
    base_currency: str | None = None,
    quote_currency: str | None = None,
    side: str | None = None,
) -> list[DailyRate]:
    return rate_repository.list_all(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
    )


def get_rate_by_id(db: Session, *, rate_id: int) -> DailyRate | None:
    return rate_repository.get_by_id(db, rate_id=rate_id)


def update_rate(db: Session, *, rate_id: int, rate: Decimal) -> DailyRate | None:
    return rate_repository.update(db, rate_id=rate_id, rate=rate)


def delete_rate(db: Session, *, rate_id: int) -> bool:
    return rate_repository.delete(db, rate_id=rate_id)
