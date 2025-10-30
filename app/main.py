from __future__ import annotations

import os
import sys
from typing import List
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import models  # noqa: F401  # ensure metadata is registered
from app.routes import api_router
from app.db.base import Base, engine


def _split_env_list(raw: str | None) -> List[str]:
    """Turn a comma separated env string into a list while handling '*' gracefully."""
    if not raw:
        return ["*"]

    cleaned = [item.strip() for item in raw.split(",") if item.strip()]
    if not cleaned:
        return ["*"]
    if cleaned == ["*"]:
        return ["*"]
    return cleaned


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


app = FastAPI(title="Ultimate App BFF", default_response_class=UTF8JSONResponse)

allow_origins = _split_env_list(os.getenv("CORS_ALLOW_ORIGINS"))
allow_methods = _split_env_list(os.getenv("CORS_ALLOW_METHODS"))
allow_headers = _split_env_list(os.getenv("CORS_ALLOW_HEADERS"))
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

app.include_router(api_router)


@app.on_event("startup")
def ensure_database_tables() -> None:
    """Create database tables if they are missing."""
    Base.metadata.create_all(bind=engine)


def run() -> None:
    """Start the FastAPI app with uvicorn. Handy for local checks."""
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=os.getenv("APP_RELOAD", "0") == "1")


if __name__ == "__main__":
    run()
