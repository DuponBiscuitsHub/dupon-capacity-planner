# DCP Raw Material Planner — Documento Maestro del Proyecto
> **Dupon · v2.0 · Planificador Primera Materia Galleta · 20/08/2026**
>
> Este documento es la fuente única de verdad del proyecto. Se actualiza en cada iteración.
> El agente IA debe leerlo al inicio de cada sesión y actualizarlo al completar tareas.

---

## 1. Visión del proyecto

Aplicación web (FastAPI + Next.js + PostgreSQL) que planifica las entregas de
primera materia de galleta (silos: harina, azúcar, aceite de coco) para Dupon.

**Arquitectura:** Backend FastAPI con PostgreSQL (Cloud SQL en producción).
Frontend Next.js. Deploy en Cloud Run. Sync periódico con Odoo vía JSON-RPC.

**Objetivo:** Calcular la fecha y hora óptima de descarga de camiones cisterna
basándose en el consumo proyectado de las líneas de galleta activas, evitando
paradas de producción por rotura de stock y rechazos de descarga por silo lleno.

**Odoo es SSoT absoluto.** La app solo cachea datos mínimos (stock, BOM, MOs, POs)
y calcula ventanas de entrega. Solo escribe `purchase.order.line.date_planned` en Odoo (D17).

**Gestión de usuarios:** 2 niveles — IT (admin) y usuario (planificador).

---

## 2. Decisiones inamovibles

| # | Decisión |
|---|----------|
| D1 | Odoo es SSoT: stock, BOM, MOs, POs, ajustes |
| D2 | DCP = cache de lectura + cálculos deterministas. Solo escribe `date_planned` en Odoo (ver D17) |
| D3 | Solo primera materia galleta. Aluminio, comercial y simulación → fase futura |
| D4 | ~~Foco Ibérica~~ → **Multicompany** (ver D12). Cada compañía Odoo = tenant en DCP |
| D5 | 5 silos Ibérica: 3 harina (25t c/u), 1 azúcar (30t), 1 aceite de coco |
| D6 | Deploy en Cloud Run + Cloud SQL (PostgreSQL) |
| D7 | Credenciales Odoo: reusar label_edge para beta. API key dedicado en prod |
| D8 | Auth segura con 2 niveles: IT (admin) y usuario |
| D9 | Recálculo de entregas: manual (botón). No automático |
| D10 | Entregas con PO+fecha confirmada no se recalculan (bloqueadas) |
| D11 | Consumos SSoT = Excel CON (kg/día por máquina), no BOMs de Odoo. BOMs probadas no fiables en rotativos |
| D12 | **Multicompany** al estilo Odoo: la app debe servir a todas las compañías del grupo. 5 companies: IBE, GUD, FRA, ITA, BEL |
| D13 | **Solo silos.** La RM en otros formatos (IBC, sacos, etc.) la gestiona Odoo con reglas de abastecimiento. DCP solo planifica silos |
| D14 | **Mock data activable** para validación de UI. Fácil de poner/quitar sin afectar producción |
| D15 | **i18n: ES, CA, EN.** Solo 3 idiomas. Claves en `translations.ts`. Sin texto hardcodeado |
| D16 | **Solo materiales de silo** en filtros UI: harina, azúcar, aceite. Sin lecitina, sal, cacao, maltitol |

---

## 3. Infraestructura (planta Ibérica)

### Silos

| Código | Material | Capacidad | Safety Stock |
|--------|----------|-----------|-------------|
| S-H1 | Harina | 25.000 kg | TBD | odoo_location_id=79, product_id=49486 |
| S-H2 | Harina | 25.000 kg | TBD | odoo_location_id=80, product_id=49486 |
| S-H3 | Harina | 25.000 kg | TBD | odoo_location_id=81, product_id=49486 |
| S-AZ | Azúcar | 30.000 kg | TBD | odoo_location_id=82, product_id=49488 |
| S-AC | Aceite de coco | TBD | TBD | odoo_location_id=83, product_id=49492 |

### Líneas de galleta

| Línea | Capacidad teórica (kg/h) | Notas |
|-------|-------------------------|-------|
| L01 | TBD | Compartida con L02 (misma RPi en label_edge) |
| L02 | TBD | Compartida con L01 |
| L03 | TBD | |
| L04 | TBD | |
| L05 | TBD | |
| L06 | TBD | |
| L07 | TBD | |
| L08 | TBD | |
| L09 | TBD | |
| L10 | TBD | |

---

## 4. Endpoints API

### Auth
- `POST /api/v1/auth/login` — Login → JWT cookie HttpOnly
- `POST /api/v1/auth/logout` — Invalidar cookie
- `GET /api/v1/auth/me` — Info usuario actual (incluye default_company_id)
- `GET /api/v1/auth/companies` — Lista compañías activas

### Silos y Entregas
- `GET /api/v1/silos` — Estado de silos con autonomía
- `GET /api/v1/silos/projection` — Proyección de stock a N días (Chart.js)
- `GET /api/v1/deliveries` — Sugerencias de entrega con estado PO
- `POST /api/v1/deliveries/recalculate` — Botón "Recalcular Entregas"

### Planificación de Entregas
- `GET /api/v1/delivery-planning` — Tabla semáforo de POs (timing + vendor)
- `POST /api/v1/delivery-planning/update-date` — Write-back `date_planned` a Odoo (IT only)

### Configuración
- `GET /api/v1/config/lines` — Líneas con capacidad teórica
- `PUT /api/v1/config/lines/{code}` — Editar capacidad (IT only)
- `GET /api/v1/config/silos` — Config de silos
- `PUT /api/v1/config/silos/{id}` — Editar silo (IT only)
- `GET /api/v1/config/recipes` — Tabla CON: consumos de referencia por formato
- `POST /api/v1/config/recipes` — Crear consumo de referencia (IT only)
- `PUT /api/v1/config/recipes/{id}` — Editar kg/día (IT only)
- `DELETE /api/v1/config/recipes/{id}` — Eliminar consumo (IT only)
- `GET /api/v1/config/line-formats` — Mapping línea → formato
- `PUT /api/v1/config/line-formats/{id}` — Editar nº máquinas (IT only)

### Correcciones y Factores
- `GET /api/v1/corrections` — Histórico de factores de corrección (últimos N días)
- `GET /api/v1/corrections/current` — Factor activo por material (para el dashboard)

### Sync
- `POST /api/v1/sync/run` — Forzar sync manual (IT only, async en thread pool)
- `GET /api/v1/sync/status` — Estado último sync
- `GET /api/v1/sync/last` — Timestamp del último sync exitoso (para label UI)
- `GET /api/v1/sync/health` — **[NUEVO v2.0]** Health check Odoo (authenticate sin sync)

### Admin (IT only)
- `GET /api/v1/admin/logs` — Últimas N líneas del log del servidor

### Usuarios (IT only)
- `GET /api/v1/users` — Listar usuarios
- `POST /api/v1/users` — Crear usuario
- `DELETE /api/v1/users/{id}` — Desactivar usuario

---

## 5. Fases de implementación

### FASE 0 — Limpieza y Documentación ✅ COMPLETADA (06/07/2026)
**Criterio:** Repo limpio. Docs actualizados. Sin código muerto del scope anterior.

- [x] Crear `.agents/AGENTS.md`
- [x] Crear `docs/proyecto_maestro.md` (este documento)
- [x] Crear `docs/architecture.md`
- [x] Crear `docs/coding_standards.md`
- [x] Archivar documentos obsoletos → `docs/archive/`
- [x] Actualizar `.gitignore`

---
### FASE 1 — Backend: Auth + Modelos + Sync ✅ COMPLETADA (06/07/2026)
**Criterio:** Código escrito y coherente. Verificación en terminal pendiente por entorno.

- [x] config.py — ODOO_MODE, SYNC_INTERVAL_SECONDS, APP_ENV
- [x] database.py — SQLite/PostgreSQL compatible (pool args condicionales)
- [x] security.py — JWT HttpOnly cookie, require_auth, require_role, validate_company_access
- [x] odoo_client.py — Síncrono (httpx.Client). Sin asyncio.run
- [x] sync_engine.py — 6 modelos Odoo, ODOO_MODE=mock short-circuit
- [x] models/odoo_replica.py — Schema reducido a galleta
- [x] models/planner.py — User, SiloConfig, LineCapacity, DeliverySuggestion, SyncLog
- [x] routers/api_auth, api_silos, api_config, api_sync, api_users
- [x] services/delivery_calculator.py — Motor determinista
- [x] services/sync_worker.py — Background asyncio worker
- [x] main.py — Lifespan, CORS, routers
- [x] tests/test_auth.py, tests/test_delivery_calculator.py
- [x] scripts/create_user.py — CLI bootstrap admin
- [x] backend/.env.example actualizado
- [x] alembic/versions/ — Migraciones 0001→0006 + setup ORM-based
- [ ] .env.test — Pendiente para tests sin interferencia del .env real

### FASE 2 — Frontend: Simplificación + Conexión Real ✅ COMPLETADA (06/07/2026)
### FASE 3 — Deploy Cloud Run ✅ COMPLETADA (06/07/2026)
### FASE 4 — Motor de Factor de Corrección ✅ COMPLETADA (06/07/2026)
### FASE 5 — Consumos Excel CON + Config UI ✅ COMPLETADA (20/07/2026)
### FASE 6 — Seguridad y Auditoría v2.0 ✅ COMPLETADA (20/08/2026)
**Criterio:** Endurecimiento de seguridad, async operations y monitoreo de salud.

- [x] JWT lifecycle: reducción a 60min expiración
- [x] RBAC multicompany: restricción de endpoints por `company_id`
- [x] Sync engine: migración a arquitectura async con thread pool para evitar bloqueos
- [x] Odoo Health Check: endpoint de monitoreo activo con indicadores visuales en UI
- [x] Migración Alembic 0004: normalización de campos de PO (`vendor_confirmed`, etc)
- [x] Script de rotación de API Key para ciclos de despliegue

### FASE 7 — Reconciliación BD y Migraciones ✅ COMPLETADA (20/08/2026)
**Criterio:** BD PostgreSQL alineada al 100% con el ORM actual. Procedimiento de setup documentado.

- [x] Migración 0005: tabla `companies` + columna `users.default_company_id`
- [x] Migración 0006: reconciliación idempotente para BD legacy → ORM actual
- [x] Corrección 0001: `workcenters` (antes `mrp_workcenters`), `purchase_orders` y `mrp_productions` alineados con ORM
- [x] Procedimiento de setup PG documentado: ORM `create_all()` + stamp Alembic
- [x] Seed data: 5 compañías Dupon + 5 silos Ibérica

---

## 6. Entorno de desarrollo

### Venv del proyecto
```
/home/pakipy/dupon-dev/dupon-capacity-planner/.venv/
```
El venv está en la raíz del mono-repo (no dentro de `backend/`).
Usar siempre `.venv/bin/python3` y `.venv/bin/pip` para instalar.

### Problema conocido: terminal cuelga al cargar config.py con .env PostgreSQL
**Causa:** `backend/.env` apunta a PostgreSQL. Al arrancar cualquier script Python que
importe `config.py`, Pydantic carga el `.env`, SQLAlchemy crea el engine y el pool
de conexiones intenta conectar → cuelga si el servidor no está levantado.

**Cómo arrancar el backend en modo mock (sin BD real ni Odoo):**
```bash
cd backend
env -i \
  DATABASE_URL="sqlite:///./dev.db" \
  JWT_SECRET="secreto_dev_32chars_minimo_ok" \
  ODOO_MODE=mock \
  APP_ENV=development \
  ../.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Cómo correr tests sin interferencia del .env real:**
```bash
cd backend
env -i \
  DATABASE_URL="sqlite:///:memory:" \
  JWT_SECRET="test_secret_32chars_minimum_ok" \
  ODOO_MODE=mock \
  ../.venv/bin/pytest app/tests/ -v
```

**Nota:** `env -i` limpia el entorno antes de arrancar, evitando que el shell
actual ya tenga variables conflictivas. Alternativa: crear `backend/.env.test`.

### Setup PostgreSQL desde cero (BD limpia)

**Procedimiento recomendado:** Crear tablas directamente desde el ORM (evita discrepancias
entre las migraciones legacy y los modelos Python actuales).

```bash
# 1. Crear BD y schemas
PGPASSWORD=<password> psql -h localhost -p 5435 -U <user> -d postgres \
  -c "DROP DATABASE IF EXISTS dcp_db_dev;"
PGPASSWORD=<password> psql -h localhost -p 5435 -U <user> -d postgres \
  -c "CREATE DATABASE dcp_db_dev;"
PGPASSWORD=<password> psql -h localhost -p 5435 -U <user> -d dcp_db_dev \
  -c "CREATE SCHEMA dcp_app; CREATE SCHEMA odoo_replica;"

# 2. Crear tablas desde ORM + stampear Alembic
cd backend
../.venv/bin/python -c "
from app.models.base import Base
import app.models.odoo_replica
import app.models.planner
from app.core.database import engine
Base.metadata.create_all(engine)
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)'))
    conn.execute(text(\"INSERT INTO alembic_version (version_num) VALUES ('0006_reconcile_pg')\"))
print('OK')
"

# 3. Seed de configuración de fábrica (SSoT: seed_config.py)
#    Inserta: 5 compañías, 5 silos, 10 líneas, 143 recetas CON, 20 mappings línea-formato
../.venv/bin/python scripts/seed_config.py

# 4. Crear admin
../.venv/bin/python -m scripts.create_user --username admin --password <password> --role it

# 5. Arrancar backend
../.venv/bin/uvicorn app.main:app --reload --port 8000
```

> **⚠️ IMPORTANTE:** `backend/scripts/seed_config.py` es la **fuente única de verdad**
> para toda la configuración de fábrica (silos, líneas, recetas CON, formatos).
> Los datos provienen del Excel `Apro-PM 2026.ods` y de IDs confirmados en Odoo staging3.
> **No modificar los valores sin verificar con el usuario.**

> **¿Por qué no `alembic upgrade head`?** Las migraciones 0001-0003 se escribieron para
> un schema anterior del proyecto. El ORM evolucionó (renombrado de tablas, columnas
> diferentes) y las migraciones no se actualizaron en paralelo. El approach ORM-based
> garantiza que la BD coincide 100% con los modelos Python.

---

## 7. Pendientes sin resolver (TBD)

| ID | Pregunta | Estado |
|----|----------|--------|
| TBD-1 | ¿Qué modelo Odoo usan para ajustes diarios de la sala de pasta? | Pendiente |
| TBD-2 | ¿Cuántas líneas tiene Gudensberg? | Pendiente (~5) |
| TBD-3 | ¿Qué location_id de Odoo corresponde a cada silo? | ✅ **Resuelto** — Silo1=79, Silo2=80, Silo3=81, Azúcar=82, Aceite=83 |
| TBD-4 | ¿Qué product_id de Odoo son harina, azúcar y aceite? | ✅ **Resuelto** — Harina=49486, Azúcar=49488, Aceite=49492 |
| TBD-5 | ¿Qué workcenter_id de Odoo son L01-L10? | Pendiente |
| TBD-6 | ¿Qué compañías del grupo van a usar DCP? | ✅ **Resuelto** — IBE, GUD, FRA, ITA, BEL |
| TBD-7 | ¿Qué silos tiene cada compañía? | Ibérica documentada (5 silos). Resto pendiente |

---

## 8. Backlog y bugs conocidos

### 🔴 Bugs
| ID | Descripción | Estado |
|----|-------------|--------|
| BUG-1 | Imágenes/visualización de silos con % de RM perdida | ✅ Resuelto |
| BUG-2 | Textos de gauges de silos solo en español (hardcodeados) | ✅ Resuelto |
| BUG-3 | Sync Odoo no refresca la pantalla tras completarse | ✅ Resuelto |

### 🟡 Pendientes técnicos
| ID | Descripción | Estado |
|----|-------------|--------|
| TECH-8 | Gráfica de evolución de consumo por silo (trend line histórico) | Pendiente — propuesta evaluada, no implementada |
| TECH-9 | `app_suggested_date` basada en cálculo real (hoy está vacía para muchas POs → timing_color siempre verde) | Pendiente — `delivery_calculator.py` no está conectado al timeline |
| TECH-10 | DeliveryPlanningTable (tabla legacy) + DeliveryTimeline coexisten — evaluar unificación | Pendiente |
| TECH-11 | Tests unitarios para `_compute_timing_color` y `_compute_editability` | Pendiente |
| TECH-12 | Alembic migration para `partner_name` y `vendor_confirmed` en `purchase_orders` (SQLite migrado manual, falta PG) | ✅ **Resuelto v2.0** — `0004_po_vendor_fields.py` |
| TECH-13 | **[NUEVO]** Multi-silo: consumo asigna 100% demanda a cada silo individual (conservador, documentar decisión) | Pendiente — decisión de diseño, no bug |
| TECH-14 | **[NUEVO]** POs replicadas en proyección: gráfica muestra un camión llenando todos los silos de un material | Pendiente — requiere lógica de asignación silo-específica |
| TECH-15 | **[NUEVO]** Rate limiter in-memory no resistente a multi-instance Cloud Run | Pendiente (Baja) — adecuado para single instance |
| TECH-16 | **[NUEVO]** Migraciones Alembic 0001-0003 desalineadas con ORM actual (tablas/columnas renombradas) | ✅ **Resuelto v2.1** — Setup ORM-based documentado. 0001 parcialmente corregido. |

---

## 9. Historial de versiones

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 06/07/2026 | v1.0 | Versión inicial. Simplificación de DCP completo a Raw Material Planner |
| 06/07/2026 | v1.1 | Fase 1 completada. Fase 2 en curso. Documentado entorno venv + problema terminal |
| 20/07/2026 | v1.2 | Fase 5 completada. Consumos basados en Excel CON (kg/día). BOM Odoo eliminada del cálculo |
| 20/07/2026 | v1.3 | Decisiones D12-D14 (multicompany, solo silos, mock data). Backlog documentado |
| 20/07/2026 | v1.4 | BUG-1 resuelto, TECH-1 (multicompany) y TECH-2 (mock data) implementados |
| 20/07/2026 | v1.5 | 5 companies (IBE/GUD/FRA/ITA/BEL). i18n: +catalán (ES/CA/EN). Filtros silo: solo harina/azúcar/aceite. D15-D16 |
| 20/07/2026 | v1.6 | Conexión Odoo staging3 verificada. TBD-3,4,6 resueltos. location_id y product_id de silos confirmados |
| 20/07/2026 | v1.7 | i18n gauges completo, CON completo, Line formats, BUG-3 resuelto |
| 20/07/2026 | v1.8 | Stock Projection, Delivery Planning, Odoo write-back, D17 |
| 20/07/2026 | v1.8b | Timeline POs, ForecastDropdown, Último sync, Pro logging |
| 20/07/2026 | v1.9 | Timeline UX, Doble semáforo, Modal edición, Fixes Python 3.10 |
| 20/07/2026 | v1.9b | Modal dual-date, partner_name sync, timing_color desacoplado, Fix prefill |
| 20/08/2026 | v2.0  | Auditoría de seguridad, Migración 0004, Sync async, Odoo Health Check, Script rotación API key |
| 20/08/2026 | v2.1  | Reconciliación BD: migraciones 0005-0006, tabla companies, setup ORM-based para PG limpio |
