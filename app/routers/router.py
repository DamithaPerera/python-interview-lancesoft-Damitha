from fastapi import APIRouter

from app.routers.rates import router as rates_router
from app.routers.transactions import router as transactions_router

api_router = APIRouter()
api_router.include_router(rates_router)
api_router.include_router(transactions_router)
