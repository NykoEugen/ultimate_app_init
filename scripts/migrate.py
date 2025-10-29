from __future__ import annotations

from app.db.base import Base, engine


def migrate() -> None:
    """Create database tables based on SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    migrate()
