"""
tests/test_auth.py — Tests de autenticación y seguridad.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models.base import Base
from app.models.planner import User

# BD en memoria para tests — StaticPool garantiza que todas las conexiones
# comparten la misma base de datos SQLite in-memory.
_TEST_DB_URL = "sqlite:///:memory:"
_engine = create_engine(
    _TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    # Strip schemas for SQLite (same as _sqlite_init)
    for table in Base.metadata.tables.values():
        table.schema = None
    Base.metadata.create_all(_engine)
    db = _TestingSessionLocal()
    # Seed: un usuario IT y uno normal
    db.add(User(username="admin", hashed_password=hash_password("Admin1234!"), role="it", is_active=True))
    db.add(User(username="planner", hashed_password=hash_password("Planner1!"), role="user", is_active=True))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ── Tests de login ────────────────────────────────────────────────────────────

def test_login_success_it(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin1234!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "it"
    assert "dcp_token" in resp.cookies


def test_login_success_user(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "planner", "password": "Planner1!"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "user"


def test_login_wrong_password(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "ghost", "password": "Ghost1234!"})
    assert resp.status_code == 401


# ── Tests de /me y logout ──────────────────────────────────────────────────────

def test_me_requires_auth(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client: TestClient):
    login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin1234!"})
    assert login.status_code == 200
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


def test_logout_clears_cookie(client: TestClient):
    client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin1234!"})
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 204


# ── Tests de RBAC ─────────────────────────────────────────────────────────────

def test_user_cannot_create_users(client: TestClient):
    client.post("/api/v1/auth/login", data={"username": "planner", "password": "Planner1!"})
    resp = client.post("/api/v1/users", json={"username": "new", "password": "Pass1234!", "role": "user"})
    assert resp.status_code == 403


def test_it_can_create_users(client: TestClient):
    client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin1234!"})
    resp = client.post("/api/v1/users", json={"username": "newuser", "password": "Pass1234!", "role": "user"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "newuser"


def test_cannot_deactivate_self(client: TestClient):
    login = client.post("/api/v1/auth/login", data={"username": "admin", "password": "Admin1234!"})
    admin_id = client.get("/api/v1/auth/me")
    # Obtener el ID del admin
    users = client.get("/api/v1/users")
    admin = next(u for u in users.json() if u["username"] == "admin")
    resp = client.delete(f"/api/v1/users/{admin['id']}")
    assert resp.status_code == 400


def test_rate_limit_blocks_after_max_attempts(client: TestClient):
    """El 6to intento fallido consecutivo retorna 429."""
    from app.routers.api_auth import _failed_attempts
    # Limpiar estado del rate limiter
    _failed_attempts.clear()

    for i in range(5):
        resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401, f"Attempt {i+1} should be 401"

    # El 6to intento debería ser bloqueado
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 429

    # Limpiar para no afectar otros tests
    _failed_attempts.clear()
