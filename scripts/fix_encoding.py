from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import sys
import os
from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file(PROJECT_ROOT / ".env")
_load_env_file(PROJECT_ROOT / ".env.local")
_load_env_file(PROJECT_ROOT / "app" / ".env")

from app.db.base import SessionLocal
from app.db.models.inventory import InventoryItemCatalog
from app.db.models.quest import Quest, QuestChoice, QuestNode


def _maybe_fix_text(value: str | None) -> tuple[str | None, bool]:
    """Return potential UTF-8 fix if the string looks like mojibake."""
    if not value:
        return value, False

    try:
        candidate_bytes = value.encode("cp1251")
    except UnicodeEncodeError:
        return value, False
    try:
        candidate = candidate_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return value, False

    if candidate == value:
        return value, False

    # Heuristic: mojibake strings are usually at least ~1.5x longer.
    if len(value) >= int(len(candidate) * 1.2):
        return candidate, True

    return value, False


def _fix_model_texts(session, model: type, fields: Iterable[str]) -> int:
    changed = 0
    entries: list[Any] = session.execute(select(model)).scalars().all()
    for entry in entries:
        entry_updated = False
        for field in fields:
            current = getattr(entry, field, None)
            fixed, updated = _maybe_fix_text(current)
            if updated:
                setattr(entry, field, fixed)
                entry_updated = True
        if entry_updated:
            changed += 1
    if changed:
        session.commit()
    return changed


def main() -> None:
    session = SessionLocal()
    try:
        total = 0
        total += _fix_model_texts(session, Quest, ("title", "description"))
        total += _fix_model_texts(session, QuestNode, ("title", "body"))
        total += _fix_model_texts(session, QuestChoice, ("label",))
        total += _fix_model_texts(session, InventoryItemCatalog, ("name", "description"))
        print(f"Updated {total} objects with repaired UTF-8 text.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
