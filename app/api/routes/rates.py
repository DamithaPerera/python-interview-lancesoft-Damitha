from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import delete_rate, list_rates, update_rate, upsert_rate
from app.db.deps import get_db
from app.models import DailyRate
from app.schemas import RateCreate, RateOut, RateUpdate

router = APIRouter(prefix="/rates", tags=["rates"])


@router.post("", response_model=RateOut)
def create_rate(payload: RateCreate, db: Session = Depends(get_db)):
    return upsert_rate(
        db,
        rate_date=payload.rate_date,
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
        rate=payload.rate,
    )


@router.get("", response_model=list[RateOut])
def get_rates(
    rate_date: date | None = Query(None),
    base_currency: str | None = Query(None),
    quote_currency: str | None = Query(None),
    side: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return list_rates(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
    )


@router.get("/{rate_id}", response_model=RateOut)
def get_rate_by_id(rate_id: int, db: Session = Depends(get_db)):
    rate = db.get(DailyRate, rate_id)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


@router.put("/{rate_id}", response_model=RateOut)
def put_rate(rate_id: int, payload: RateUpdate, db: Session = Depends(get_db)):
    rate = update_rate(db, rate_id=rate_id, rate=payload.rate)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


@router.delete("/{rate_id}")
def remove_rate(rate_id: int, db: Session = Depends(get_db)):
    ok = delete_rate(db, rate_id=rate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rate not found")
    return {"deleted": True}
