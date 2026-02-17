#!/bin/sh
set -e

echo "Preparing database migrations..."

python - <<'PY'
import os
import subprocess
import sys
from sqlalchemy import create_engine, inspect, text

db_url = os.getenv("DATABASE_URL", "sqlite:///./fx.db")
engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {})
inspector = inspect(engine)

tables = set(inspector.get_table_names())
app_tables = {"daily_rates", "fx_transactions", "fx_quotes"}
has_app_tables = bool(tables.intersection(app_tables))
has_alembic_table = "alembic_version" in tables

alembic_has_revision = False
if has_alembic_table:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
        alembic_has_revision = row is not None and bool(row[0])

if has_alembic_table and alembic_has_revision:
    print("alembic_version with revision found; running upgrade head.")
    sys.exit(0)

if has_app_tables and (not has_alembic_table or not alembic_has_revision):
    print("Legacy schema detected; stamping head.")
    subprocess.run(["alembic", "stamp", "head"], check=True)
    sys.exit(0)

print("No schema detected; fresh upgrade will run.")
PY

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
