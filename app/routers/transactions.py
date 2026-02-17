from fastapi import APIRouter

from app.controllers import transactions_controller
from app.schemas import TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])

router.post("", response_model=TransactionOut)(
    transactions_controller.create_fx_transaction
)
router.post(
    "/confirm",
    response_model=TransactionOut,
    summary="Confirm a previously generated quote and persist transaction",
    responses={
        404: {"description": "Quote not found"},
        409: {"description": "Quote already confirmed"},
        422: {"description": "Quote expired"},
    },
)(transactions_controller.confirm_fx_transaction)
