from __future__ import annotations

from fastapi import FastAPI

from app.routers.router import api_router

app = FastAPI(title="Money Changer API")
app.include_router(api_router)
