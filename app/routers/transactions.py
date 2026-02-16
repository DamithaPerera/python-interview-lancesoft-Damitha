from fastapi import APIRouter

from app.controllers import transactions_controller
from app.schemas import TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])

router.post("", response_model=TransactionOut)(
    transactions_controller.create_fx_transaction
)
