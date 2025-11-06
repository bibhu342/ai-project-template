#!/usr/bin/env sh
set -e

# run migrations on container start (skip if SKIP_MIGRATIONS=1)
if [ "$SKIP_MIGRATIONS" != "1" ]; then
  alembic upgrade head
fi

# start API
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
