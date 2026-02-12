from __future__ import annotations

from datetime import date
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

import crud
from db import Base, SessionLocal, engine
from models import DailyRate
from schemas import RateCreate, RateOut, RateUpdate, TransactionCreate, TransactionOut
from services import get_calculator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Money Changer API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/rates", response_model=RateOut)
def create_rate(payload: RateCreate, db: Session = Depends(get_db)):
    rate = crud.upsert_rate(
        db,
        rate_date=payload.rate_date,
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
        rate=payload.rate,
    )
    return rate


@app.get("/rates", response_model=list[RateOut])
def list_rates(
    rate_date: date | None = Query(None),
    base_currency: str | None = Query(None),
    quote_currency: str | None = Query(None),
    side: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return crud.list_rates(
        db,
        rate_date=rate_date,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
    )


@app.get("/rates/{rate_id}", response_model=RateOut)
def get_rate(rate_id: int, db: Session = Depends(get_db)):
    rate = db.get(DailyRate, rate_id)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


@app.put("/rates/{rate_id}", response_model=RateOut)
def update_rate(rate_id: int, payload: RateUpdate, db: Session = Depends(get_db)):
    rate = crud.update_rate(db, rate_id=rate_id, rate=payload.rate)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")
    return rate


@app.delete("/rates/{rate_id}")
def delete_rate(rate_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_rate(db, rate_id=rate_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rate not found")
    return {"deleted": True}


@app.post("/transactions", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    rate = crud.get_rate(
        db,
        rate_date=payload.timestamp.date(),
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
    )
    if not rate:
        raise HTTPException(status_code=422, detail="No daily rate for transaction date")

    calc = get_calculator(payload.side)
    result = calc.calculate(
        rate=rate.rate,
        foreign_amount=payload.foreign_amount,
        base_amount=payload.base_amount,
    )

    txn = crud.create_transaction(
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