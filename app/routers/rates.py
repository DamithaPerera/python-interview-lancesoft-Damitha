from fastapi import APIRouter

from app.controllers import rates_controller
from app.schemas import RateOut

router = APIRouter(prefix="/rates", tags=["rates"])

router.post("", response_model=RateOut)(rates_controller.create_rate)
router.get("", response_model=list[RateOut])(rates_controller.list_rates)
router.get("/{rate_id}", response_model=RateOut)(rates_controller.get_rate)
router.put("/{rate_id}", response_model=RateOut)(rates_controller.put_rate)
router.delete("/{rate_id}")(rates_controller.remove_rate)
