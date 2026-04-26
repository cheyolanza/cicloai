#!/usr/bin/env sh
set -eu

run_migrations="${RUN_DB_MIGRATIONS:-true}"
run_seed="${RUN_DB_SEED:-true}"

if [ "$run_migrations" = "true" ]; then
  echo "[startup] Running database migrations: alembic upgrade head"
  alembic upgrade head
else
  echo "[startup] Skipping database migrations because RUN_DB_MIGRATIONS=$run_migrations"
fi

if [ "$run_seed" = "true" ]; then
  echo "[startup] Running idempotent database seed"
  python -m cicloai.infrastructure.database.seed
else
  echo "[startup] Skipping database seed because RUN_DB_SEED=$run_seed"
fi

echo "[startup] Starting FastAPI with Uvicorn"
exec uvicorn cicloai.interfaces.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
