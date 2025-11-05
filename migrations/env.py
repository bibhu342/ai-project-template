from __future__ import annotations

import os
import sys
from pathlib import Path
import importlib.util
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

"""
Make the repository's local "app" package resolvable even if a 3rd‑party
package named "app" is preinstalled in the environment (common on CI).

Strategy:
- Prepend the repo root to sys.path so our local packages are found first.
- If a foreign "app" module is already imported, remove it from sys.modules
  so the subsequent import picks up our local package.
"""
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# If a third-party "app" module was imported earlier, drop it to avoid
# shadowing our local package (which lives at PROJECT_ROOT / "app").
if "app" in sys.modules:
    try:
        # Only drop it if it's not our local package path
        mod = sys.modules["app"]
        mod_file = getattr(mod, "__file__", "") or ""
        if "ai-project-template" not in mod_file.replace("\\", "/"):
            del sys.modules["app"]
    except Exception:
        # On any ambiguity, prefer deleting to let import resolve fresh
        del sys.modules["app"]

# Force-load our local "app" package so submodule imports resolve under it.
# This avoids accidentally importing a third-party package named "app".
app_init_path = PROJECT_ROOT / "app" / "__init__.py"
if app_init_path.exists():
    spec = importlib.util.spec_from_file_location("app", str(app_init_path))
    if spec and spec.loader:
        app_module = importlib.util.module_from_spec(spec)
        # Point package path to the local app directory so "app.*" imports work
        app_module.__path__ = [str(app_init_path.parent)]  # type: ignore[attr-defined]
        sys.modules["app"] = app_module
        spec.loader.exec_module(app_module)


# Now that we've ensured "app" is our local package, import normally
from app.database import Base  # noqa: E402

# Import models to register them on Base.metadata
import app.models  # noqa: F401, E402 - registers models on Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

# Read DB URL from env (Docker compose sets this)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://bibhu:supersecure@localhost:5432/ai_lab",
)
# Ensure alembic sees the URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
