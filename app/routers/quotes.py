from fastapi import APIRouter

from app.controllers import quotes_controller
from app.schemas import QuoteOut

router = APIRouter(prefix="/quotes", tags=["quotes"])

router.post(
    "",
    response_model=QuoteOut,
    summary="Create a quote",
    description=(
        "Calculate and persist a quote using the daily rate for the payload date.\n\n"
        "Use the returned `quote_id` with `POST /transactions/confirm` to commit.\n\n"
        "Important: Provide exactly one of `foreign_amount` or `base_amount`.\n"
        "If both or neither are provided, request validation fails with 422."
    ),
    responses={
        422: {
            "description": (
                "Validation error (both/neither amount fields) "
                "or no daily rate for the transaction date."
            )
        }
    },
)(quotes_controller.get_quote)
