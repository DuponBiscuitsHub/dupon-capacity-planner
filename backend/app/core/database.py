from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")


def _build_engine():
    """Construye el engine SQLAlchemy según el DATABASE_URL configurado.

    SQLite (dev/tests): sin pool, sin schemas.
    PostgreSQL (producción): pool con pre-ping para detectar conexiones muertas.
    """
    if _IS_SQLITE:
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
    return create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _sqlite_init() -> None:
    """Inicialización de BD SQLite: strip schemas + create_all + seed companies.

    Se llama explícitamente desde el lifespan de main.py solo cuando
    DATABASE_URL apunta a SQLite. En PostgreSQL nunca se ejecuta.

    SQLite no soporta schemas. Eliminamos el atributo schema de todas las
    tablas para que SQLAlchemy genere SQL sin prefijo.
    """
    from app.models.base import Base
    import app.models.odoo_replica  # noqa — registrar modelos en Base.metadata
    import app.models.planner       # noqa — registrar modelos en Base.metadata

    for table in Base.metadata.tables.values():
        table.schema = None

    Base.metadata.create_all(engine)
    _seed_companies_if_empty()


def _seed_companies_if_empty() -> None:
    """Inserta las 5 compañías del grupo Dupon si la tabla está vacía.

    Idempotente: solo inserta si no hay registros.
    Se usa en SQLite dev init y en el lifespan de PostgreSQL como safety net.
    """
    from app.models.planner import Company

    db = SessionLocal()
    try:
        if db.query(Company).count() > 0:
            return

        _COMPANIES = [
            Company(id=1, name="Dupon Biscuits Ibérica SAU", odoo_company_id=1, short_code="IBE"),
            Company(id=2, name="Dupon Biscuits Gudensberg", odoo_company_id=2, short_code="GUD"),
            Company(id=3, name="Dupon Biscuits France", odoo_company_id=3, short_code="FRA"),
            Company(id=4, name="Dupon Biscuits Italia", odoo_company_id=4, short_code="ITA"),
            Company(id=5, name="Dupon Biscuits Belgium", odoo_company_id=5, short_code="BEL"),
        ]
        db.add_all(_COMPANIES)
        db.commit()
    finally:
        db.close()


def get_db():
    """Generador de sesión de BD para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
