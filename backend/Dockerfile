# ── Backend Dockerfile ─────────────────────────────────────────────────────
# Multi-stage: build (deps) + runtime (slim).
# Target: Cloud Run. Puerto configurado por env $PORT (default 8000).
# ──────────────────────────────────────────────────────────────────────────

# ── Stage 1: deps ─────────────────────────────────────────────────────────
FROM python:3.10-slim AS deps

# psycopg2 necesita libpq-dev en build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

# psycopg2 necesita libpq en runtime
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias del stage anterior
COPY --from=deps /install /usr/local

# Usuario sin privilegios (seguridad: no correr como root en Cloud Run)
RUN adduser --disabled-password --gecos "" appuser
USER appuser

WORKDIR /app

# Copiar solo el código de la app (no tests, no scripts, no .env)
COPY --chown=appuser:appuser app/ ./app/

# Cloud Run inyecta PORT como variable de entorno
ENV PORT=8000

# Alembic migrations se corren por separado en el entrypoint de Cloud Run Jobs
# o manualmente antes del primer deploy.
# No correr alembic aquí para mantener imagen stateless.

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"]
