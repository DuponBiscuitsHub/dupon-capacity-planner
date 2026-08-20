"""
app/core/security.py — Autenticación JWT y RBAC.

Responsabilidades:
  - hash_password / verify_password (bcrypt)
  - create_access_token (JWT firmado)
  - decode_access_token (verifica firma y expiración)
  - require_auth (dependencia FastAPI: extrae JWT de la cookie)
  - require_role (dependencia FastAPI: verifica rol)

Paradigma: Funcional — sin estado entre llamadas.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

_logger = logging.getLogger("app.security")

_COOKIE_NAME = "dcp_token"


# rounds reducidos en dev para login rápido; 12 en producción (seguridad)
_BCRYPT_ROUNDS: int = 4 if settings.APP_ENV in ("development", "test") else 12


def hash_password(password: str) -> str:
    """Genera bcrypt hash. Rounds: 4 en dev, 12 en prod."""
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica contraseña contra su hash bcrypt."""
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception as exc:
        _logger.warning("Password verification error: %s", exc)
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(user_id: int, role: str) -> str:
    """Genera un JWT firmado con HS256 (dev) / RS256 (prod).

    Args:
        user_id: ID de la tabla users.
        role: 'it' o 'user'.

    Returns:
        JWT string listo para Set-Cookie.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verifica firma y expiración del JWT.

    Returns:
        Payload dict con 'sub' y 'role'.

    Raises:
        HTTPException 401: Si el token es inválido o ha expirado.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


# ── Dependencias FastAPI ───────────────────────────────────────────────────────

def require_auth(
    dcp_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """Dependencia: extrae y valida el JWT de la cookie HttpOnly.

    Inyecta el payload del token en el endpoint. Uso:
        current_user: dict = Depends(require_auth)

    Raises:
        HTTPException 401: Si no hay cookie o el token es inválido.
    """
    if not dcp_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    payload = decode_access_token(dcp_token)

    # Verificar que el usuario sigue activo en BD
    from app.models.planner import User
    user = db.query(User).filter(
        User.id == int(payload["sub"]),
        User.is_active.is_(True),
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )
    # Devolvemos el payload enriquecido con datos de BD para los endpoints
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "default_company_id": user.default_company_id,
    }


def require_role(role: str):
    """Factory de dependencia para restringir endpoints a un rol.

    Uso:
        _: dict = Depends(require_role("it"))

    Args:
        role: 'it' para admin-only.
    """
    def _check(current_user: dict = Depends(require_auth)) -> dict:
        if current_user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required.",
            )
        return current_user
    return _check
