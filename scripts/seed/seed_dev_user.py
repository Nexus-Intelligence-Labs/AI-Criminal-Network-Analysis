"""Create a local development user without exposing or replacing credentials."""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import app.models  # noqa: F401  Register all model metadata.
from app.core.security import hash_password
from app.db.postgres import get_engine
from app.models.user import Base, User
from sqlalchemy import select


def main() -> int:
    username = os.getenv("DEVELOPMENT_ADMIN_USERNAME") or input(
        "Development username: "
    ).strip()
    password = os.getenv("DEVELOPMENT_ADMIN_PASSWORD") or getpass.getpass(
        "Development password: "
    )

    if not username or not password:
        print("Username and password are required.", file=sys.stderr)
        return 2

    engine = get_engine()
    Base.metadata.create_all(engine)

    with engine.begin() as connection:
        existing = connection.execute(
            select(User.id).where(User.username == username)
        ).first()
        if existing:
            print(f"Development user already exists: {username}")
            return 0

        connection.execute(
            User.__table__.insert().values(
                username=username,
                password_hash=hash_password(password),
            )
        )

    print(f"Created development user: {username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
