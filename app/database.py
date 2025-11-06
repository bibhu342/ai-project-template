# app/database.py
from __future__ import annotations

import os
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# Read from env. In docker compose, this is already set.
# Use file-based SQLite for testing to avoid database pollution
_testing = os.getenv("TESTING", "false").lower() == "true"
if _testing:
    # Always use SQLite for tests, ignore DATABASE_URL from .env
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://bibhu:supersecure@postgres:5432/ai_lab",
    )

# Use check_same_thread=False for SQLite to work with FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# Define naming convention for constraints and indexes
# This ensures consistent naming across environments and prevents Alembic drift
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
