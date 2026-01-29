#!/bin/bash
set -e

echo "=== FinConnect Backend Startup ==="

# 1. Applica le migrazioni del database
echo "[1/3] Applicazione migrazioni database..."
alembic upgrade head

# 2. Popola il database con dati demo (se vuoto)
echo "[2/3] Verifica e popolamento dati demo..."
python seed_data.py

# 3. Avvia il server FastAPI
echo "[3/3] Avvio server FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
