#!/bin/bash
# restart_dev.sh — Para, re-seedea y arranca el backend en modo mock (SQLite)
# Uso: bash restart_dev.sh
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJECT_ROOT/.venv/bin"
BACKEND="$PROJECT_ROOT/backend"

echo "🔪 Matando procesos uvicorn..."
pkill -f "uvicorn app.main" 2>/dev/null || true
sleep 1

echo "🌱 Sembrando datos de prueba (silos + CON + POs)..."
cd "$PROJECT_ROOT"
env -i \
  DATABASE_URL="sqlite:///$BACKEND/dev.db" \
  JWT_SECRET="secreto_dev_32chars_minimo_ok_ok" \
  ODOO_MODE=mock \
  APP_ENV=development \
  "$VENV/python3" seed_dev_data.py

echo ""
echo "👤 Asegurando usuario IT de desarrollo..."
cd "$BACKEND"
env -i \
  DATABASE_URL="sqlite:///./dev.db" \
  JWT_SECRET="secreto_dev_32chars_minimo_ok_ok" \
  ODOO_MODE=mock \
  APP_ENV=development \
  "$VENV/python" -m scripts.create_user \
    --username it_admin --password DuponIT2026 --role it 2>/dev/null || true

echo ""
echo "🚀 Arrancando backend en puerto 8000..."
echo "   Usuario: it_admin / DuponIT2026"
echo "   Frontend: http://localhost:3000"
echo "   API docs: http://localhost:8000/api/docs"
echo ""
cd "$BACKEND"
env -i \
  HOME="$HOME" \
  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  DATABASE_URL="sqlite:///./dev.db" \
  JWT_SECRET="secreto_dev_32chars_minimo_ok_ok" \
  ODOO_MODE=mock \
  APP_ENV=development \
  "$VENV/uvicorn" app.main:app --port 8000
