from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas import QuoteCreate
from app.services.business import create_quote


def get_quote(payload: QuoteCreate, db: Session = Depends(get_db)):
    quote = create_quote(db, payload=payload)
    if not quote:
        raise HTTPException(status_code=422, detail="No daily rate for transaction date")
    return quote
