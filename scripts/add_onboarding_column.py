#!/usr/bin/env python3
from __future__ import annotations

from sqlalchemy import inspect, text

from app.db.base import engine


def main() -> None:
    with engine.begin() as connection:
        inspector = inspect(connection)
        existing_columns = {col["name"] for col in inspector.get_columns("players")}
        if "onboarding_completed" not in existing_columns:
            connection.execute(
                text("ALTER TABLE players ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE")
            )
            connection.execute(
                text("UPDATE players SET onboarding_completed = FALSE WHERE onboarding_completed IS NULL")
            )
            print("Column onboarding_completed added to players table.")
        else:
            print("Column onboarding_completed already exists. No changes applied.")


if __name__ == "__main__":
    main()
