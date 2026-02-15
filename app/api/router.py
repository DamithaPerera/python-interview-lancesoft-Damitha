from fastapi import APIRouter

from app.api.routes.rates import router as rates_router
from app.api.routes.transactions import router as transactions_router

api_router = APIRouter()
api_router.include_router(rates_router)
api_router.include_router(transactions_router)
