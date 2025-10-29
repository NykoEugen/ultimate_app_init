from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from fastapi import FastAPI

from app.routes import api_router
from app.db.base import Base, engine


app = FastAPI(title="Ultimate App BFF")
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
