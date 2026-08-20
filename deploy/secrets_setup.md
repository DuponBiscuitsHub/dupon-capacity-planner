# deploy/secrets_setup.md — Configuración inicial de GCP Secret Manager

## Secretos requeridos en producción

Antes del primer deploy, crear estos secretos en GCP Secret Manager:

```bash
# Database URL completa (Cloud SQL Proxy format)
echo "postgresql://dcp_user:CONTRASEÑA@/dcp_db?host=/cloudsql/PROYECTO:REGION:INSTANCIA" | \
  gcloud secrets create dcp-database-url --data-file=-

# JWT signing key (≥32 chars, aleatorio)
openssl rand -base64 48 | gcloud secrets create dcp-jwt-secret --data-file=-

# Odoo API key (obtener de Odoo > Settings > API Keys)
echo "TU_ODOO_API_KEY" | gcloud secrets create dcp-odoo-api-key --data-file=-
```

## Permisos requeridos

La service account de Cloud Run necesita el rol `Secret Manager Secret Accessor`:

```bash
gcloud secrets add-iam-policy-binding dcp-database-url \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Repetir para dcp-jwt-secret y dcp-odoo-api-key
```

## Variables de entorno NO secretas (se pasan en el deploy directamente)

| Variable | Valor prod |
|----------|-----------|
| `ODOO_MODE` | `real` |
| `APP_ENV` | `production` |
| `SYNC_INTERVAL_SECONDS` | `900` |
| `ODOO_URL` | `https://tu-odoo.com` |
| `ODOO_DB` | `nombre_bd_odoo` |
| `ODOO_USER` | `usuario_api_odoo` |
| `ODOO_TIMEOUT_SECONDS` | `15` |
