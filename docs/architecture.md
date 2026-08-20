# DCP Raw Material Planner — Arquitectura Técnica

> **v2.0 · 21/07/2026** — Referencia de diseño para devs y agentes IA.
> Leer una vez. Consultar cuando haya dudas de "por qué" algo está así.

---

## 1. Visión en 30 segundos

```
┌──────────┐   JSON-RPC (read-only)   ┌──────────────────────────────────┐
│  Odoo    │ ◄────────────────────── │  Cloud Run: FastAPI + PostgreSQL  │
│  (SSoT)  │ ───────────────────►    │  Sync cada 15 min                │
│          │  BOM, MOs, Stock,       │  Motor de cálculo de entregas    │
│          │  POs, Ajustes           │  Auth JWT + RBAC (IT / usuario)  │
└──────────┘                         └───────────┬────────────────────────┘
                                                  │ REST JSON
                                     ┌────────────▼───────────────────┐
                                     │  Cloud Run: Next.js Frontend    │
                                     │  Silos + Entregas + Config      │
                                     └────────────────────────────────┘
```

**En una frase:** Odoo tiene los datos → DCP los cachea y calcula cuándo pedir camiones → el planificador revisa y actúa en Odoo.

---

## 2. Principios de arquitectura

### 2.1. Odoo es SSoT absoluto

La app **no** es un ERP. No gestiona MOs, turnos, operarios ni productos.
Solo cachea datos mínimos para calcular ventanas de entrega.

**Por qué:** Si la app almacenara lógica de negocio, tendríamos dos fuentes de verdad
y un infierno de sincronización.

### 2.2. Escritura limitada a `date_planned`

La app solo escribe **un campo** en Odoo: `purchase.order.line.date_planned`.
Todo lo demás es read-only. Las recomendaciones de entrega se validan
por el planificador antes de modificar la fecha en la PO.

**Por qué:** Minimizar riesgo transaccional. Human-in-the-loop. Solo se escribe
lo imprescindible para que el proveedor reciba la fecha correcta.

### 2.3. Recálculo bajo demanda

Las sugerencias de entrega no se calculan continuamente. El planificador pulsa
un botón "Recalcular" cuando los datos están listos (después de los ajustes
de la sala de pasta).

**Por qué:** El flujo operativo real es: ajustar consumos (6-9 AM) → recalcular → actuar.
Un cálculo continuo produciría ruido sobre datos no calibrados.

### 2.4. Multicompañía

El Odoo de Dupon es multicompany. Cada petición al backend incluye `company_id`.
El frontend tiene un selector de planta en el header.

**Por qué:** Preparar la extensión a Gudensberg y otras plantas sin refactoring.

---

## 3. Capas del código

```
┌────────────────────────────────────────────────────────────────┐
│  Routers (backend/app/routers/)                                │
│  Responsabilidad: HTTP request/response, validación            │
│  Regla: queries simples OK; lógica compleja → services         │
├────────────────────────────────────────────────────────────────┤
│  Services (backend/app/services/)                              │
│  Responsabilidad: lógica de negocio, acceso a BD               │
│  Regla: NO devolver HTTPException ni Response                  │
├────────────────────────────────────────────────────────────────┤
│  Models (backend/app/models/)                                  │
│  Responsabilidad: schema BD (SQLAlchemy ORM)                   │
│  Regla: solo definición de tablas, sin lógica                  │
├────────────────────────────────────────────────────────────────┤
│  Core (backend/app/core/)                                      │
│  Responsabilidad: config, database, security, odoo_client      │
│  Regla: sin lógica de negocio específica de silos              │
└────────────────────────────────────────────────────────────────┘
```

### Mapa de ficheros por capa

| Capa | Fichero | Responsabilidad |
|------|---------|-----------------|
| **Core** | `config.py` | Settings (Pydantic BaseSettings) |
| **Core** | `database.py` | Engine, SessionLocal, get_db |
| **Core** | `security.py` | JWT, bcrypt, require_auth, require_role |
| **Core** | `odoo_client.py` | JSON-RPC 2.0 client (authenticate, search_read, write) |
| **Core** | `sync_engine.py` | Orquestador de sync: pull modelos de Odoo → upsert local |
| **Router** | `api_auth.py` | POST /auth/login, /auth/logout, GET /auth/me, /auth/companies |
| **Router** | `api_silos.py` | GET /silos, /silos/projection, GET/POST /deliveries |
| **Router** | `api_config.py` | GET/PUT /config/lines, /config/silos |
| **Router** | `api_corrections.py` | GET /corrections, CRUD /config/recipes, /config/line-formats |
| **Router** | `api_delivery_planning.py` | GET /delivery-planning, POST /update-date (write-back Odoo) |
| **Router** | `api_sync.py` | POST /sync/run, GET /sync/status, GET /sync/last |
| **Router** | `api_users.py` | CRUD usuarios (IT only) |
| **Router** | `api_admin.py` | GET /admin/logs (IT only) |
| **Service** | `delivery_calculator.py` | Motor de cálculo: stock − consumo CON = ventana descarga |
| **Service** | `delivery_planning.py` | Cruce POs vs fechas sugeridas, semáforo timing+vendor |
| **Service** | `stock_projection.py` | Proyección diaria de stock a N días (Chart.js) |
| **Service** | `correction_engine.py` | Auto-calibración: factor = consumo_real / consumo_teórico |
| **Service** | `sync_worker.py` | Background worker asyncio (start/stop en lifespan) |
| **Model** | `odoo_replica.py` | Cache Odoo (7 modelos): products, stock_quants, mrp_boms, mrp_bom_lines, workcenters, mrp_productions, purchase_orders |
| **Model** | `planner.py` | Datos app (10 modelos): Company, User, SiloConfig, LineCapacity, DeliverySuggestion, SyncLog, RefConsumptionRate, LineFormat, ProductFormatMapping, CorrectionFactor |

---

## 4. Flujos principales

### 4.a. Sync periódico (cada 15 min)

```
sync_worker._sync_loop()   (asyncio background task)
        │
        ├─ 1. sync_products()        → cache productos primera materia
        ├─ 2. sync_workcenters()     → cache líneas de galleta
        ├─ 3. sync_stock_quants()    → niveles de silos (filtro location_id)
        ├─ 4. sync_manufacturing()   → MOs activas/planificadas
        ├─ 5. sync_purchase_orders() → POs de primera materia
        └─ 6. log_sync()            → audit trail en sync_log
```

### 4.b. Recalcular entregas (botón del planificador)

```
POST /api/v1/deliveries/recalculate
        │
        ▼
delivery_calculator.recalculate(company_id)
        │
        ├─ 1. Leer stock actual de cada silo (stock_quants, filtro location_id)
        ├─ 2. Leer consumos de tabla CON (ref_consumption_rates: kg_per_day × machines)
        ├─ 3. Aplicar factor de corrección auto-calibrado (correction_engine)
        ├─ 4. Calcular consumo_horario = Σ(kg_per_day × machines / 24) × factor
        ├─ 5. Calcular ventana_descarga: (stock - safety) / consumo - 4h margen
        ├─ 6. Buscar POs existentes → asignar estado
        ├─ 7. NO tocar entregas con status='confirmed' (🔒)
        └─ 8. Guardar delivery_suggestions en BD
```

### 4.c. Login

```
POST /api/v1/auth/login {username, password}
        │
        ├─ 1. Buscar user en tabla users
        ├─ 2. Verificar password (bcrypt)
        ├─ 3. Generar JWT (sub=user_id, role=it|user, exp=60min)
        ├─ 4. Set-Cookie: dcp_token=<jwt>; HttpOnly; Secure; SameSite=Strict
        └─ 5. Response: {username, role}
```

---

## 5. Base de datos

### 5.1. Schema `odoo_replica` (cache de Odoo)

| Tabla | PK | Campos clave | Registros típicos |
|-------|----|-------------|-------------------|
| `products` | odoo_id | name, default_code, company_id | ~100 (primera materia) |
| `stock_quants` | odoo_id | product_id, location_id, quantity, company_id | ~50 (silos) |
| `mrp_boms` | odoo_id | product_id, quantity, company_id | ~30 (recetas galleta) |
| `mrp_bom_lines` | odoo_id | bom_id, product_id, product_qty | ~200 (líneas BOM) |
| `mrp_productions` | odoo_id | product_id, qty_to_produce, state, date_planned_start, company_id | ~50 (MOs activas) |
| `workcenters` | odoo_id | name, code, capacity_nominal, company_id | ~15 (líneas galleta) |
| `purchase_orders` | odoo_id | product_id, quantity, date_planned, state, company_id | ~30 (POs MP) |

### 5.2. Schema `dcp_app` (datos propios)

| Tabla | PK | Campos clave | Registros típicos |
|-------|----|-------------|-------------------|
| `companies` | id | name, odoo_company_id, short_code, is_active | 5 (IBE/GUD/FRA/ITA/BEL) |
| `users` | id | username, hashed_password, role (it/user), is_active, default_company_id | ~10 |
| `silo_configs` | id | silo_code, name, material_type, capacity_kg, safety_stock_kg, odoo_location_id, odoo_product_id, company_id | 5 (Ibérica) |
| `line_capacities` | id | line_code, capacity_kg_h, company_id, updated_by | 10 (L01-L10) |
| `delivery_suggestions` | id | silo_code, suggested_date, qty_kg, status, po_odoo_id, company_id | Crece con recálculos |
| `sync_log` | id | model_name, status, records_synced, timestamp | Crece con syncs |
| `ref_consumption_rates` | id | format_code, material_type, kg_per_day, company_id, updated_by | ~170 (14 formatos × 11 materiales) |
| `correction_factors` | id | date, material_type, factor, stock_expected/actual, company_id | Crece (1/día/material) |
| `line_formats` | id | line_code, format_code, machines, company_id | ~20 (línea→formato) |
| `product_format_mappings` | id | odoo_product_id, format_code, company_id | Pendiente de poblar |

### 5.3. Estados de delivery_suggestions

```
draft (⚪) ──► po_pending (🟡) ──► confirmed (✅🔒) ──► delivered (📦)
   │                                    ▲
   └── Recalcular las renueva          │ No se toca en recálculo
```

---

## 6. Seguridad

| Capa | Mecanismo | Detalle |
|------|-----------|---------| 
| **Auth** | JWT + cookie HttpOnly | Firmado HS256 (dev) / RS256 (prod). Cookie Secure+SameSite=Strict |
| **RBAC** | Middleware `require_role()` | `it` = admin total. `user` = operar (ver, recalcular) |
| **Passwords** | bcrypt | Hasheadas en BD. Nunca en logs |
| **Odoo API Key** | .env / Secret Manager | Nunca en código ni en frontend |
| **SQL** | SQLAlchemy ORM | Parametrizado siempre. Nunca concatenación de strings |
| **CORS** | Whitelist explícita | Solo orígenes del frontend |

---

## 7. Stack tecnológico

| Componente | Tecnología | Versión | Por qué |
|-----------|-----------|---------|---------|
| Runtime backend | Python | 3.11+ | Type hints maduros. FastAPI compatible |
| Framework backend | FastAPI | 0.100+ | Async-ready, Pydantic, OpenAPI auto-docs |
| BD | PostgreSQL | 15 | Cloud SQL. Relacional. Robusto |
| ORM | SQLAlchemy | 2.x | Estándar de facto |
| Migrations | Alembic | 1.x | Versionado de schema |
| HTTP client (Odoo) | httpx | 0.24+ | Async/sync. JSON-RPC |
| Auth | PyJWT + bcrypt | — | Estándar. Sin dependencias pesadas |
| Frontend | Next.js | 15+ | SSR, App Router, TypeScript |
| Styling | Vanilla CSS Modules | — | Sin dependencia de framework CSS |
| Deploy | Cloud Run + Cloud SQL | — | Serverless. Escala a cero |
| Secretos | GCP Secret Manager | — | Producción. .env para dev |

---

## 8. Estructura de directorios

```
dupon-capacity-planner/
├── .agents/
│   └── AGENTS.md                # Reglas para agentes IA
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, lifespan, routers
│   │   ├── core/
│   │   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   │   ├── database.py      # Engine, SessionLocal, get_db
│   │   │   ├── security.py      # JWT, bcrypt, require_auth, require_role
│   │   │   ├── odoo_client.py   # JSON-RPC 2.0 client
│   │   │   └── sync_engine.py   # Orquestador de sync Odoo → local
│   │   ├── models/
│   │   │   ├── odoo_replica.py  # Cache Odoo (7 tablas)
│   │   │   └── planner.py       # Datos app (5 tablas)
│   │   ├── routers/
│   │   │   ├── api_auth.py
│   │   │   ├── api_silos.py
│   │   │   ├── api_config.py
│   │   │   ├── api_corrections.py
│   │   │   ├── api_delivery_planning.py
│   │   │   ├── api_sync.py
│   │   │   ├── api_users.py
│   │   │   └── api_admin.py
│   │   ├── services/
│   │   │   ├── delivery_calculator.py
│   │   │   ├── delivery_planning.py
│   │   │   ├── stock_projection.py
│   │   │   ├── correction_engine.py
│   │   │   └── sync_worker.py
│   │   └── tests/
│   ├── alembic/
│   ├── scripts/
│   │   └── create_user.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx       # Sidebar + Header
│   │   │   ├── page.tsx         # Dashboard resumen
│   │   │   ├── silos/page.tsx   # Panel SCADA + entregas + recalcular
│   │   │   └── config/page.tsx  # Config líneas, silos, usuarios (IT)
│   │   ├── login/page.tsx
│   │   └── i18n/                # ES + CA + EN (3 idiomas)
│   ├── Dockerfile
│   └── package.json
├── docs/
│   ├── proyecto_maestro.md      # SSoT del proyecto
│   ├── architecture.md          # Este documento
│   ├── coding_standards.md
│   └── archive/                 # Docs históricos
├── docker-compose.yml
└── .env.example
```

---

## 9. Decisiones de diseño y "por qué"

| # | Decisión | Por qué |
|---|----------|---------| 
| D1 | Odoo SSoT | Evitar doble fuente de verdad. App = cache + cálculo |
| D2 | Read-only | Fase inicial. Sin riesgo transaccional. Human-in-the-loop |
| D3 | Recálculo manual | El flujo real es: calibrar → recalcular → actuar. No continuo |
| D4 | PostgreSQL (no SQLite) | Cloud SQL para Cloud Run. Concurrencia. Schemas separados |
| D5 | JWT en cookie HttpOnly | Más seguro que localStorage. Sin XSS. Sin document.cookie |
| D6 | 2 roles (IT/user) | Mínimo viable. Sin sobreingeniería RBAC |
| D7 | Sync cada 15 min | Balance entre frescura y carga en Odoo. Configurable |
| D8 | JSON-RPC (no REST) | API estándar de Odoo. OdooClient ya implementado y probado |
| D9 | CSS Modules (no Tailwind) | Consistencia con label_edge. Control total. Sin dependencia |
| D10 | Multicompañía desde D1 | Evitar refactoring cuando Gudensberg se añada |
