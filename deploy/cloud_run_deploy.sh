#!/usr/bin/env bash
# deploy/cloud_run_deploy.sh
# ──────────────────────────────────────────────────────────────────────────
# Script de deploy manual en Cloud Run (backend + frontend).
# Prerequisitos:
#   - gcloud CLI instalado y autenticado
#   - Proyecto GCP configurado: gcloud config set project $GCP_PROJECT
#   - Cloud SQL instance creada con la BD dcp_db
#   - Secrets configurados en GCP Secret Manager (JWT_SECRET, ODOO_API_KEY...)
#
# Uso:
#   chmod +x deploy/cloud_run_deploy.sh
#   GCP_PROJECT=mi-proyecto REGION=europe-west1 ./deploy/cloud_run_deploy.sh
# ──────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuración ──────────────────────────────────────────────────────────
GCP_PROJECT="${GCP_PROJECT:?Definir GCP_PROJECT}"
REGION="${REGION:-europe-west1}"
REPO="eu.gcr.io/${GCP_PROJECT}"     # Artifact Registry o Container Registry
BACKEND_IMAGE="${REPO}/dcp-backend"
FRONTEND_IMAGE="${REPO}/dcp-frontend"
CLOUD_SQL_INSTANCE="${GCP_PROJECT}:${REGION}:dcp-postgres"

# ── Build y push backend ───────────────────────────────────────────────────
echo "▶ Building backend image..."
docker build -t "${BACKEND_IMAGE}:latest" ./backend
docker push "${BACKEND_IMAGE}:latest"

echo "▶ Deploying backend to Cloud Run..."
gcloud run deploy dcp-backend \
  --image "${BACKEND_IMAGE}:latest" \
  --region "${REGION}" \
  --platform managed \
  --no-allow-unauthenticated \
  --add-cloudsql-instances "${CLOUD_SQL_INSTANCE}" \
  --set-secrets \
    "DATABASE_URL=dcp-database-url:latest,JWT_SECRET=dcp-jwt-secret:latest,ODOO_API_KEY=dcp-odoo-api-key:latest" \
  --set-env-vars \
    "ODOO_MODE=real,APP_ENV=production,SYNC_INTERVAL_SECONDS=900,ODOO_TIMEOUT_SECONDS=15" \
  --min-instances 0 \
  --max-instances 3 \
  --memory 512Mi \
  --cpu 1

# Obtener la URL del backend para pasársela al frontend
BACKEND_URL=$(gcloud run services describe dcp-backend \
  --region "${REGION}" --format "value(status.url)")
echo "✅ Backend URL: ${BACKEND_URL}"

# ── Build y push frontend ──────────────────────────────────────────────────
echo "▶ Building frontend image (NEXT_PUBLIC_API_URL=${BACKEND_URL})..."
docker build \
  --build-arg "NEXT_PUBLIC_API_URL=${BACKEND_URL}" \
  -t "${FRONTEND_IMAGE}:latest" \
  ./frontend
docker push "${FRONTEND_IMAGE}:latest"

echo "▶ Deploying frontend to Cloud Run..."
gcloud run deploy dcp-frontend \
  --image "${FRONTEND_IMAGE}:latest" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "NODE_ENV=production,PORT=3000" \
  --min-instances 0 \
  --max-instances 2 \
  --memory 256Mi \
  --cpu 1

FRONTEND_URL=$(gcloud run services describe dcp-frontend \
  --region "${REGION}" --format "value(status.url)")
echo "✅ Frontend URL: ${FRONTEND_URL}"

echo ""
echo "🚀 Deploy completado:"
echo "   Backend:  ${BACKEND_URL}"
echo "   Frontend: ${FRONTEND_URL}"
echo ""
echo "⚠️  Recuerda correr la migración inicial si es el primer deploy:"
echo "   gcloud run jobs create dcp-migrate \\"
echo "     --image ${BACKEND_IMAGE}:latest \\"
echo "     --region ${REGION} \\"
echo "     --set-secrets 'DATABASE_URL=dcp-database-url:latest' \\"
echo "     --command 'alembic' --args 'upgrade,head'"
