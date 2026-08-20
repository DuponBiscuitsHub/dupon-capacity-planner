"""
scripts/create_user.py — CLI para crear el primer usuario IT.

Uso:
  cd backend
  python -m scripts.create_user --username admin --password MiClave123 --role it
"""
import argparse
import sys

sys.path.insert(0, ".")

from app.core.database import SessionLocal, _IS_SQLITE, _sqlite_init
from app.core.security import hash_password
from app.models.planner import User

# En modo SQLite (dev/tests), inicializar la BD antes de usarla.
# En PostgreSQL esto es no-op.
if _IS_SQLITE:
    _sqlite_init()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a DCP user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True, help="Min 8 characters")
    parser.add_argument("--role", required=True, choices=["it", "user"])
    args = parser.parse_args()

    if len(args.password) < 8:
        print("ERROR: Password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == args.username).first()
        if existing:
            print(f"ERROR: Username '{args.username}' already exists.", file=sys.stderr)
            sys.exit(1)

        user = User(
            username=args.username,
            hashed_password=hash_password(args.password),
            role=args.role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"✅ User '{args.username}' created with role '{args.role}'.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
