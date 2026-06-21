"""
Database wiring for the FastAPI service.

Connects to the SAME Postgres + SAME `business_items` table as Django.
We deliberately do NOT call Base.metadata.create_all(): the schema is owned
by db/init.sql. SQLAlchemy only maps onto the existing table.
"""
# Core
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://portal:portal@db:5432/portal"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
