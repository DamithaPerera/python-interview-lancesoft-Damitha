from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DailyRate


def get_rate(
    db: Session,
    *,
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
) -> DailyRate | None:
    stmt = select(DailyRate).where(
        DailyRate.rate_date == rate_date,
        DailyRate.base_currency == base_currency,
        DailyRate.quote_currency == quote_currency,
        DailyRate.side == side,
    )
    return db.execute(stmt).scalar_one_or_none()


def upsert_rate(
    db: Session,
    *,
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
    rate: Decimal,
) -> DailyRate:
    existing = get_rate(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
    )
    if existing:
        existing.rate = rate
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    new_rate = DailyRate(
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
        rate=rate,
    )
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return new_rate


def list_rates(
    db: Session,
    *,
    rate_date: date | None = None,
    base_currency: str | None = None,
    quote_currency: str | None = None,
    side: str | None = None,
) -> list[DailyRate]:
    stmt = select(DailyRate)
    if rate_date:
        stmt = stmt.where(DailyRate.rate_date == rate_date)
    if base_currency:
        stmt = stmt.where(DailyRate.base_currency == base_currency)
    if quote_currency:
        stmt = stmt.where(DailyRate.quote_currency == quote_currency)
    if side:
        stmt = stmt.where(DailyRate.side == side)
    return list(db.execute(stmt).scalars().all())


def update_rate(db: Session, *, rate_id: int, rate: Decimal) -> DailyRate | None:
    rate_obj = db.get(DailyRate, rate_id)
    if not rate_obj:
        return None
    rate_obj.rate = rate
    db.add(rate_obj)
    db.commit()
    db.refresh(rate_obj)
    return rate_obj


def delete_rate(db: Session, *, rate_id: int) -> bool:
    rate_obj = db.get(DailyRate, rate_id)
    if not rate_obj:
        return False
    db.delete(rate_obj)
    db.commit()
    return True
