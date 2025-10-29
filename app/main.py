from __future__ import annotations

from fastapi import FastAPI

from app.routes import api_router


app = FastAPI(title="Ultimate App BFF")
app.include_router(api_router)
