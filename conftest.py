# Ensure our local 'app' package is imported instead of any third-party package
# named 'app' that may be present in the environment (e.g., on CI images).
from __future__ import annotations

import sys
import os
from pathlib import Path
import importlib.util
import pytest

# Set testing environment variable BEFORE any imports
os.environ["TESTING"] = "true"

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# If some foreign 'app' is already imported, drop it to avoid shadowing
if "app" in sys.modules:
    try:
        mod = sys.modules["app"]
        mod_file = getattr(mod, "__file__", "") or ""
        if str(PROJECT_ROOT).replace("\\", "/") not in mod_file.replace("\\", "/"):
            del sys.modules["app"]
    except Exception:
        del sys.modules["app"]

# Explicitly load our local 'app' package from path to guarantee resolution
app_init_path = PROJECT_ROOT / "app" / "__init__.py"
if app_init_path.exists():
    spec = importlib.util.spec_from_file_location(
        "app",
        str(app_init_path),
        submodule_search_locations=[str(app_init_path.parent)],
    )
    if spec and spec.loader:
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = app_module
        spec.loader.exec_module(app_module)


def pytest_configure(config):
    """Initialize test database before any tests run."""
    import pathlib
    from datetime import datetime, timezone

    # Import database module to ensure TESTING env var is checked
    from app import database

    # Import all models to register them with SQLAlchemy
    from app.models import user  # noqa: F401
    from app.models import customer  # noqa: F401
    from app.models import note  # noqa: F401

    # Add SQLite compatibility for PostgreSQL functions
    if str(database.engine.url).startswith("sqlite"):
        from sqlalchemy import event

        @event.listens_for(database.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Add custom PostgreSQL-compatible functions to SQLite."""
            cursor = dbapi_conn.cursor()
            # Enable foreign key constraints in SQLite
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

            # Add now() function
            dbapi_conn.create_function(
                "now", 0, lambda: datetime.now(timezone.utc).isoformat()
            )
            # Add true/false for boolean defaults
            dbapi_conn.create_function("true", 0, lambda: 1)
            dbapi_conn.create_function("false", 0, lambda: 0)

    # Clean up old test database if it exists
    test_db = pathlib.Path("test.db")
    if test_db.exists():
        try:
            test_db.unlink()
        except PermissionError:
            pass  # File is locked, will be overwritten

    # Create all tables
    database.Base.metadata.create_all(bind=database.engine)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    """Cleanup test database after all tests complete."""
    import pathlib
    from app.database import engine, Base

    yield

    # Cleanup after all tests
    test_db = pathlib.Path("test.db")
    try:
        engine.dispose()  # Close all connections first
        Base.metadata.drop_all(bind=engine)
        if test_db.exists():
            test_db.unlink()
    except (PermissionError, Exception):
        pass  # Best effort cleanup


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """Clean all data from tables before each test."""
    from app import database
    from app.models import note, customer, user

    yield  # Run the test first

    # Clean up after test
    with database.SessionLocal() as db:
        db.query(note.Note).delete()
        db.query(customer.Customer).delete()
        db.query(user.User).delete()
        db.commit()


@pytest.fixture(scope="module")
def client():
    """Provide a test client for each test module."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
