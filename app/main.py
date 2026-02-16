from __future__ import annotations

from fastapi import FastAPI

from app.routers.router import api_router
from app.db import Base, engine
from app import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Money Changer API")
app.include_router(api_router)
