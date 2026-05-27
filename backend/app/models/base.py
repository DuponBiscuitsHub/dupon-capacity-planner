from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Shared Declarative Base class for all database models.
    Supports SQLAlchemy 2.0 standards and type mapping.
    """
    pass
