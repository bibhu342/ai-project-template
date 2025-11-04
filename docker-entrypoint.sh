#!/usr/bin/env sh
set -e

# run migrations on container start
alembic upgrade head

# start API
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
