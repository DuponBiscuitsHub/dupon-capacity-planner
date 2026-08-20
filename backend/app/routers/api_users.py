"""
app/routers/api_users.py — CRUD de usuarios (IT only).

GET    /api/v1/users       — Listar usuarios activos
POST   /api/v1/users       — Crear usuario
DELETE /api/v1/users/{id}  — Desactivar usuario (soft delete)
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, require_role
from app.models.planner import User

_logger = logging.getLogger("app.users")

router = APIRouter(prefix="/api/v1/users", tags=["users"])

_VALID_ROLES = {"it", "user"}


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=8)
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in _VALID_ROLES:
            raise ValueError(f"Role must be one of: {_VALID_ROLES}")
        return v


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[UserOut])
def list_users(
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    """Lista todos los usuarios (activos e inactivos). Solo IT."""
    users = db.query(User).order_by(User.username).all()
    return [UserOut(id=u.id, username=u.username, role=u.role, is_active=u.is_active) for u in users]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> UserOut:
    """Crea un nuevo usuario. Solo IT."""
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.username}' already exists.",
        )

    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # No loguear el password nunca
    _logger.info("User created", extra={"username": user.username, "role": user.role, "by": current_user["username"]})
    return UserOut(id=user.id, username=user.username, role=user.role, is_active=user.is_active)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    current_user: dict = Depends(require_role("it")),
    db: Session = Depends(get_db),
) -> None:
    """Desactiva un usuario (soft delete). Solo IT."""
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_active = False
    db.commit()
    _logger.info("User deactivated", extra={"user_id": user_id, "by": current_user["username"]})
