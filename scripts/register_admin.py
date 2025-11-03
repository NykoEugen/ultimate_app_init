from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models.user import UserAccount
from app.utils.security import create_password_digest


def _normalize_login(raw: str) -> str:
    value = raw.strip().lower()
    if not value:
        raise ValueError("Логін не може бути порожнім.")
    return value


def register_admin(login: str, password: str) -> None:
    normalized_login = _normalize_login(login)

    salt, digest = create_password_digest(password)

    with SessionLocal() as session:
        existing = session.execute(select(UserAccount).where(UserAccount.login == normalized_login)).scalars().first()
        if existing is not None:
            raise ValueError(f"Користувач із логіном '{normalized_login}' вже існує.")

        admin = UserAccount(
            login=normalized_login,
            password_hash=digest,
            password_salt=salt,
            is_admin=True,
            player_id=None,
        )
        session.add(admin)
        session.commit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Реєстрація адміністратора для Ultimate App")
    parser.add_argument("--login", help="Логін адміністратора (обов'язковий)")
    parser.add_argument("--password", help="Пароль адміністратора (небезпечно передавати у відкритому вигляді)")
    args = parser.parse_args(argv)

    login = args.login or input("Введіть логін адміністратора: ").strip()
    if not login:
        print("Логін обов'язковий.", file=sys.stderr)
        return 1

    password = args.password or getpass.getpass("Введіть пароль адміністратора: ")
    if not password:
        print("Пароль обов'язковий.", file=sys.stderr)
        return 1

    try:
        register_admin(login, password)
    except ValueError as exc:
        print(f"Помилка: {exc}", file=sys.stderr)
        return 1

    print(f"Адміністратора '{login.strip().lower()}' успішно зареєстровано.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
