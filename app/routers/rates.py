from fastapi import APIRouter

from app.controllers import rates_controller
from app.schemas import RateOut

router = APIRouter(prefix="/rates", tags=["rates"])

router.post(
    "",
    response_model=RateOut,
    summary="Create daily rate",
    responses={409: {"description": "Rate already exists for the composite key"}},
)(rates_controller.create_rate)
router.get("", response_model=list[RateOut])(rates_controller.list_rates)
router.get(
    "/{rate_date}/{base_currency}/{quote_currency}/{side}", response_model=RateOut
)(rates_controller.get_rate)
router.put(
    "/{rate_date}/{base_currency}/{quote_currency}/{side}", response_model=RateOut
)(rates_controller.put_rate)
router.delete("/{rate_date}/{base_currency}/{quote_currency}/{side}")(
    rates_controller.remove_rate
)
