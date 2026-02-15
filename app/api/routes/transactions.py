from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import create_transaction, get_rate
from app.db.deps import get_db
from app.schemas import TransactionCreate, TransactionOut
from app.services import get_calculator

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut)
def create_fx_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    rate = get_rate(
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

    txn = create_transaction(
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
