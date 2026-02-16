from __future__ import annotations

from datetime import date

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import RateCreate, RateUpdate
from app.services.business import (
    create_or_update_rate,
    delete_rate,
    get_rate_by_key,
    get_rates,
    update_rate,
)


def create_rate(payload: RateCreate, db: Session = Depends(get_db)):
    return create_or_update_rate(
        db,
        rate_date=payload.rate_date,
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
        rate=payload.rate,
    )


def list_rates(
    rate_date: date | None = Query(None),
    base_currency: str | None = Query(None),
    quote_currency: str | None = Query(None),
    side: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return get_rates(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
    )


def get_rate(
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
    db: Session = Depends(get_db),
):
    rate = get_rate_by_key(
        db,
        rate_date=rate_date,
        base_currency=base_currency.upper(),
        quote_currency=quote_currency.upper(),
        side=side.upper(),
    )
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


def put_rate(
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
    payload: RateUpdate,
    db: Session = Depends(get_db),
):
    rate = update_rate(
        db,
        rate_date=rate_date,
        base_currency=base_currency.upper(),
        quote_currency=quote_currency.upper(),
        side=side.upper(),
        rate=payload.rate,
    )
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


def remove_rate(
    rate_date: date,
    base_currency: str,
    quote_currency: str,
    side: str,
    db: Session = Depends(get_db),
):
    ok = delete_rate(
        db,
        rate_date=rate_date,
        base_currency=base_currency.upper(),
        quote_currency=quote_currency.upper(),
        side=side.upper(),
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Rate not found")
    return {"deleted": True}
