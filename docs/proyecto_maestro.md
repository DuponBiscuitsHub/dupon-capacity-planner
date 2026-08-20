# DCP Raw Material Planner — Documento Maestro del Proyecto
> **Dupon · v1.9b · Planificador Primera Materia Galleta · 21/07/2026**
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
- `POST /api/v1/sync/run` — Forzar sync manual (IT only)
- `GET /api/v1/sync/status` — Estado último sync
- `GET /api/v1/sync/last` — Timestamp del último sync exitoso (para label UI)

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
- [x] security.py — JWT HttpOnly cookie, require_auth, require_role
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
- [ ] alembic/versions/ — **Migración inicial pendiente** (bloqueada hasta arrancar con PG)
- [ ] .env.test — Pendiente para tests sin interferencia del .env real

---

### FASE 2 — Frontend: Simplificación + Conexión Real ✅ COMPLETADA (06/07/2026)
**Criterio:** Frontend conectado a backend real. Silos y entregas funcionales.

- [x] layout.tsx — auth real via /me, logout correcto, nav simplificado (ES+EN)
- [x] translations.ts — Solo ES+EN, claves DCP, archivo reescrito desde cero
- [x] login/page.tsx — POST form-encoded, credentials:'include'
- [x] silos/page.tsx — API real, fill bars SCADA, tabla entregas, botón recalcular
- [x] (dashboard)/page.tsx — Overview: stat cards + mini silo cards + acciones rápidas
- [x] config/page.tsx — Panel IT: 3 tabs (líneas, silos, usuarios)
- [x] Modules fuera de scope — aluminum, commercial, simulation → stub redirect
- [x] frontend/.env.local — NEXT_PUBLIC_API_URL configurado

---

### FASE 3 — Deploy Cloud Run ✅ COMPLETADA (06/07/2026)
**Criterio:** Artefactos de deploy listos. Pendiente ejecución en GCP.

- [x] backend/Dockerfile — Multi-stage, non-root, Cloud Run compatible
- [x] frontend/Dockerfile — Multi-stage, Next.js standalone output
- [x] next.config.ts — output: 'standalone' activado
- [x] docker-compose.yml — Stack local completo (PG + backend + frontend)
- [x] alembic/versions/0001_initial.py — Migración inicial con seed Ibérica
- [x] deploy/cloud_run_deploy.sh — Script deploy backend + frontend
- [x] deploy/secrets_setup.md — Guía GCP Secret Manager

**Para ejecutar el deploy:**
```bash
GCP_PROJECT=mi-proyecto REGION=europe-west1 ./deploy/cloud_run_deploy.sh
```


---

### FASE 4 — Motor de Factor de Corrección ✅ COMPLETADA (06/07/2026)
**Criterio:** App auto-calibra el consumo real vs. teórico de Odoo. Tabla CON como fallback.

- [x] `models/planner.py` — `RefConsumptionRate` (tabla CON) + `CorrectionFactor`
- [x] `alembic/versions/0002_correction_factors.py` — Migración + seed 60 filas CON
- [x] `services/correction_engine.py` — Motor auto-calibración: stock_expected vs stock_actual
- [x] `services/delivery_calculator.py` — Fallback CON + factor de corrección aplicado
- [x] `core/database.py` — SQLite compat: strip schemas + create_all en lifespan
- [x] `routers/api_corrections.py` — 4 endpoints: historial + current + recipes CRUD
- [x] `services/sync_worker.py` — Llama correction_engine.run() tras cada sync
- [x] `(dashboard)/page.tsx` — Sección "Factores de corrección activos" con color coding
- [x] `config/page.tsx` — Tab 4 "Recetas (CON)" con grid editable

**Modelo de cálculo:**
```
stock_expected = stock_ayer + entradas_hoy - consumo_teórico_odoo
consumption_actual = stock_ayer + entradas_hoy - stock_actual_odoo
factor = consumption_actual / consumption_teórico
```

**Invariantes:**
- Odoo SSoT: el ajuste de sala de pasta se hace en Odoo, la app solo lo lee
- La app nunca escribe en Odoo
- Factor se auto-calibra diariamente tras el sync
- Sanity clamp: factor fuera de [0.50, 2.00] se ignora → usa 1.0

---

### FASE 5 — Consumos Excel CON + Config UI ✅ COMPLETADA (20/07/2026)
**Criterio:** Consumos basados en Excel CON (kg/día por máquina). BOM Odoo eliminada del cálculo. Config editable por IT.

- [x] Análisis comparativo BOM vs Excel: HAAS consistente, rotativos/Oreo/BC divergen
- [x] Decisión arquitectural: D11 — Excel CON es SSoT para consumos
- [x] `models/planner.py` — `RefConsumptionRate` evolucionado: `format_code`, `kg_per_day`, `updated_by`
- [x] `models/planner.py` — Nueva tabla `LineFormat` (línea→formato, nº máquinas)
- [x] `models/planner.py` — Nueva tabla `ProductFormatMapping` (producto Odoo→formato)
- [x] `alembic/versions/0003_kg_per_day.py` — Migración + seed ~170 filas CON + 20 line_formats
- [x] `services/delivery_calculator.py` — Simplificado: elimina BOM Odoo, usa `kg_per_day × machines / 24`
- [x] `routers/api_corrections.py` — Endpoints actualizados: CRUD recetas + line-formats
- [x] `config/page.tsx` — Tab "Recetas (kg/día)" actualizada con 11 ingredientes
- [x] `config/page.tsx` — Nuevo tab "Líneas ↔ Formatos" con edición de máquinas

**Modelo de cálculo v2:**
```
consumption_kg_h = Σ (kg_per_day × machines / 24)   # por cada línea/formato
corrected = consumption_kg_h × correction_factor
```

**Datos seed incluidos:**
- 14 formatos: STD_R_110, STD_R_SS, HAAS_110, HAAS_98, HAAS_98_OREO, HAAS_110_OREO, MINI_75_SS, MINI_75_OLI, MINI_82, MINI_82_OREO, MINI_90, MINI_90_SS, IMPERIAL, BONCOLAC
- 11 ingredientes: harina, azucar, aceite, lecitina, sal, carbonat, caramelina, maltitol, cacao, colorante, oli_bany
- 20 mappings línea→formato con máquinas (L01_L02=8, L06=8, L03-L10=1)

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
| BUG-1 | Imágenes/visualización de silos con % de RM perdida | ✅ Resuelto (era falta de seed data) |
| BUG-2 | Textos de gauges de silos solo en español (hardcodeados) | ✅ Resuelto v1.7 — `t()` + nuevas claves i18n |
| BUG-3 | Sync Odoo no refresca la pantalla tras completarse | ✅ Resuelto v1.7 — estado `refreshing` separado |

### 🟡 Pendientes técnicos
| ID | Descripción | Estado |
|----|-------------|--------|
| TECH-1 | Multicompany (D12): selector de compañía, datos por tenant | ✅ Implementado |
| TECH-2 | Mock data (D14): seed_dev_data.py con companies, silos, stock, CON | ✅ Eliminado — datos reales desde Odoo |
| TECH-3 | Migración Alembic limpia (0001→0003 consolidar si es posible) | Pendiente (Baja) |
| TECH-4 | product_format_mappings vacía (TBD-4 bloquea) | Pendiente (Baja) |
| TECH-5 | i18n: textos nuevos de Fase 5 sin traducir (LineFormatsTab) | ✅ Resuelto v1.7 |
| TECH-6 | Recetas CON: 8 ingredientes nuevos con valor 0 (sin datos Excel) | ✅ Resuelto v1.7 — valores reales extraídos |
| TECH-7 | Tipos de línea rotativa/lineal no visibles en UI Config | ✅ Resuelto v1.7 — badge + bloqueo edición |

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
| 20/07/2026 | v1.7 | **i18n gauges completo** (matHarina/matAzucar/matAceite + locales BCP-47). **CON completo** (11 materiales × 13 formatos desde Excel Apro-PM 2026.ods). **Line formats** rotativa vs lineal: badges en UI + bloqueo edición en hornos lineales. **BUG-3**: sync refresca pantalla (estado `refreshing` independiente). |
| 20/07/2026 | v1.8 | **Stock Projection Chart** en Dashboard (Chart.js, forward-looking 14 días). **Delivery Planning Table** en Silos (semáforo green/orange/red POs vs fecha sugerida). **Odoo write-back** de `date_planned` vía JSON-RPC con restricciones por estado (draft=libre, purchase=warning, done=bloqueado). **D17**: cambio scope read-only → write limitado a `purchase.order.line.date_planned`. Dropdown forecast 15/30/45 días. `odoo_product_id` poblado en silo_configs. `order_odoo_id` añadido a PurchaseOrder. |
| 20/07/2026 | v1.8b | **Timeline POs reales**: DeliveryTimeline ahora muestra POs de Odoo con semáforo. Botón edición integrado en pill. **ForecastDropdown** (15/30/45 días). **Último sync**: `GET /sync/last` + label relativo en header. **Pro logging**: `RotatingFileHandler` → `logs/dcp.log` (5MB×3). `GET /admin/logs` endpoint (role=it). |
| 20/07/2026 | v1.9 | **Timeline UX completo**: pill = toda la tarjeta clicable (sin lápiz), hover effect scale+brightness. **Doble semáforo visual**: fondo=timing (verde=a tiempo/naranja=tarde/rojo=sin PO) + borde-izquierdo=vendor_confirmed (verde=confirmado proveedor/rojo=pendiente). **vendor_confirmed**: nuevo campo `purchase.order.vendor_confirmed` leído desde Odoo, persistido en `purchase_orders.vendor_confirmed`. **Modal edición rediseñado**: chips proveedor+ref RM, +20% tamaño, gradient buttons, spring animation. **Fix Python 3.10**: `datetime.fromisoformat()` con sufijo `Z` → `.replace("Z", "+00:00")`. **Fix `fmtKg`**: acepta `number \| null`. **i18n**: `silosSyncNever`, `silosSyncJustNow`. |
| 20/07/2026 | v1.9b | **Modal dual-date**: campo "Fecha Sugerida" (read-only, calculada por app) + "Fecha PO" (editable, la actual de Odoo). Botón "↓ Usar propuesta" copia la fecha sugerida al campo editable. **partner_name en PO**: sync lee `partner_id` de `purchase.order` y guarda nombre del proveedor. **product_ref en modal**: `[default_code] product_name` desde relación `Product`. **timing_color desacoplado**: nuevo campo API `timing_color` (green/orange/red) independiente de `vendor_confirmed`. Antes `_compute_color` mezclaba ambos ejes → las POs con `vendor_confirmed=false` siempre daban rojo aunque tuvieran PO. **Fix prefill**: `openEdit()` ahora prefilla con `po_date_planned` (fecha real Odoo), no `app_suggested_date`. **i18n**: `planUseSuggested`, `planNoSuggested`. |

---

## 10. Pendientes para próxima sesión

### 🔴 Bugs
| ID | Descripción | Prioridad |
|----|-------------|-----------|
| BUG-4 | **Selector de compañía desaparecido.** Causa raíz: la tabla `companies` nunca tenía seed data. `GET /auth/companies` devolvía `[]` → condición `companies.length > 1` siempre false. Fix: `_seed_companies_if_empty()` en `database.py`. | ✅ Resuelto v1.9b |

### 🟡 Pendientes técnicos
| ID | Descripción | Estado |
|----|-------------|--------|
| TECH-8 | Gráfica de evolución de consumo por silo (trend line histórico) | Pendiente — propuesta evaluada, no implementada |
| TECH-9 | `app_suggested_date` basada en cálculo real (hoy está vacía para muchas POs → timing_color siempre verde) | Pendiente — `delivery_calculator.py` no está conectado al timeline |
| TECH-10 | DeliveryPlanningTable (tabla legacy) + DeliveryTimeline coexisten — evaluar unificación | Pendiente |
| TECH-11 | Tests unitarios para `_compute_timing_color` y `_compute_editability` | Pendiente |
| TECH-12 | Alembic migration para `partner_name` y `vendor_confirmed` en `purchase_orders` (SQLite migrado manual, falta PG) | Pendiente |
