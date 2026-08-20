"""
app/routers/api_auth.py — Endpoints de autenticación.

POST /api/v1/auth/login   — Valida credenciales, emite JWT en cookie HttpOnly.
POST /api/v1/auth/logout  — Invalida la cookie.
GET  /api/v1/auth/me      — Devuelve datos del usuario autenticado.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    require_auth,
    verify_password,
)
from app.models.planner import Company, User

_logger = logging.getLogger("app.auth")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

_COOKIE_NAME = "dcp_token"
# SameSite=Strict protege contra CSRF. Secure=True en producción (HTTPS only).
_COOKIE_OPTS: dict = {
    "httponly": True,
    "samesite": "strict",
    "secure": settings.APP_ENV == "production",
    "max_age": 3600,  # 60 min, alineado con ACCESS_TOKEN_EXPIRE_MINUTES
}

# ── Rate limiting (brute-force protection) ──────────────────────────────────
# In-memory: adecuado para single-instance Cloud Run.
# Key: username → list of failed attempt timestamps (últimos _RL_WINDOW_S segundos).
import time
from collections import defaultdict

_RL_MAX_ATTEMPTS = 5
_RL_WINDOW_S = 900  # 15 minutos
_failed_attempts: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(username: str) -> None:
    """Lanza 429 si el username ha superado el límite de intentos fallidos."""
    now = time.monotonic()
    bucket = _failed_attempts[username]
    # Purgar intentos fuera de la ventana
    _failed_attempts[username] = [t for t in bucket if now - t < _RL_WINDOW_S]
    if len(_failed_attempts[username]) >= _RL_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )


def _record_failed_attempt(username: str) -> None:
    """Registra un intento fallido para el rate limiter."""
    _failed_attempts[username].append(time.monotonic())


class LoginResponse(BaseModel):
    username: str
    role: str
    default_company_id: int | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Autentica al usuario y emite un JWT en cookie HttpOnly.

    Usa OAuth2PasswordRequestForm para recibir username y password
    como application/x-www-form-urlencoded (estándar de seguridad).
    """
    _check_rate_limit(form_data.username)

    user = db.query(User).filter(
        User.username == form_data.username,
        User.is_active.is_(True),
    ).first()

    # Verificar siempre aunque user sea None para evitar timing attacks
    password_ok = verify_password(
        form_data.password, user.hashed_password if user else "dummy"
    )
    if not user or not password_ok:
        _record_failed_attempt(form_data.username)
        _logger.warning(
            "Failed login attempt",
            extra={"username": form_data.username},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )


    token = create_access_token(user_id=user.id, role=user.role)
    response.set_cookie(_COOKIE_NAME, token, **_COOKIE_OPTS)

    _logger.info("User logged in", extra={"username": user.username, "role": user.role})
    return LoginResponse(
        username=user.username,
        role=user.role,
        default_company_id=user.default_company_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """Invalida la cookie del cliente eliminándola."""
    response.delete_cookie(_COOKIE_NAME, samesite="strict")


@router.get("/me", response_model=LoginResponse)
def me(current_user: dict = Depends(require_auth)) -> LoginResponse:
    """Devuelve el usuario actualmente autenticado."""
    return LoginResponse(
        username=current_user["username"],
        role=current_user["role"],
        default_company_id=current_user.get("default_company_id"),
    )


# ── Companies ─────────────────────────────────────────────────────────────────

class CompanyOut(BaseModel):
    id: int
    name: str
    short_code: str | None
    is_active: bool


@router.get("/companies", response_model=list[CompanyOut])
def list_companies(
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
) -> list[CompanyOut]:
    """Lista todas las compañías activas."""
    rows = db.query(Company).filter(Company.is_active.is_(True)).all()
    return [
        CompanyOut(id=c.id, name=c.name, short_code=c.short_code, is_active=c.is_active)
        for c in rows
    ]
