from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import TransactionCreate
from app.services.business import create_transaction


def create_fx_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = create_transaction(db, payload=payload)
    if not transaction:
        raise HTTPException(status_code=422, detail="No daily rate for transaction date")
    return transaction
