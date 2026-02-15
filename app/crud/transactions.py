from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import FxTransaction


def create_transaction(
    db: Session,
    *,
    timestamp,
    base_currency: str,
    quote_currency: str,
    side: str,
    foreign_amount: Decimal,
    base_amount: Decimal,
    effective_rate: Decimal,
    fee_amount: Decimal,
    rounding_adjustment: Decimal,
) -> FxTransaction:
    txn = FxTransaction(
        transaction_timestamp=timestamp,
        base_currency=base_currency,
        quote_currency=quote_currency,
        side=side,
        foreign_amount=foreign_amount,
        base_amount=base_amount,
        effective_rate=effective_rate,
        fee_amount=fee_amount,
        rounding_adjustment=rounding_adjustment,
    )
    db.add(txn)
    db.flush()
    txn.transaction_id = f"TXN-{timestamp.strftime('%Y%m%d')}-{txn.id:06d}"
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn
