from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import TransactionConfirmCreate, TransactionCreate
from app.services.business import confirm_transaction, create_transaction


def create_fx_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = create_transaction(db, payload=payload)
    if not transaction:
        raise HTTPException(status_code=422, detail="No daily rate for transaction date")
    return transaction


def confirm_fx_transaction(
    payload: TransactionConfirmCreate, db: Session = Depends(get_db)
):
    transaction = confirm_transaction(db, payload=payload)
    if transaction == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Quote not found")
    if transaction == "ALREADY_CONFIRMED":
        raise HTTPException(status_code=409, detail="Quote already confirmed")
    if transaction == "EXPIRED":
        raise HTTPException(status_code=422, detail="Quote expired")
    return transaction
