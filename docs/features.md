# DCP Raw Material Planner — Guía de Características y Funcionalidades

> **Dupon Biscuits · v2.0 · Julio 2026**
>
> Documento de referencia para agentes IA, desarrolladores y stakeholders.
> Describe **todas** las funcionalidades implementadas y planificadas.

---

## 1. Resumen Ejecutivo

**DCP Raw Material Planner** es una aplicación web que planifica las entregas de primera materia (harina, azúcar, aceite de coco) para las fábricas de galleta de Dupon.

**Objetivo**: Calcular la fecha y hora óptima de descarga de camiones cisterna en los silos de producción, evitando:
- Paradas de producción por rotura de stock
- Rechazos de descarga por silo lleno

**Stack**: FastAPI + PostgreSQL (backend) · Next.js (frontend) · Cloud Run + Cloud SQL (deploy)

**Principio fundamental**: **Odoo es SSoT absoluto**. La app solo cachea datos mínimos y calcula ventanas de entrega. No reemplaza al ERP.

---

## 2. Autenticación y Autorización

### 2.1. Login JWT con Cookie HttpOnly

| Aspecto | Detalle |
|---------|---------|
| **Mecanismo** | JWT firmado con HS256, almacenado en cookie HttpOnly (no accesible desde JS) |
| **Expiración** | Configurable vía `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60 = 1h) |
| **Hash contraseña** | bcrypt (4 rounds dev / 12 rounds prod) |
| **Endpoints** | `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me` |

### 2.2. RBAC — 2 Roles

| Rol | Código | Permisos |
|-----|--------|----------|
| **IT (Admin)** | `it` | Todo: gestión usuarios, config silos/líneas/recetas, sync forzado, logs |
| **Usuario (Planificador)** | `user` | Ver dashboard, silos, entregas, recalcular entregas |

**Implementación**: Dependencias FastAPI `require_auth` y `require_role("it")`. Todo endpoint protegido.

### 2.3. Gestión de Usuarios (IT only)

- Listar usuarios activos
- Crear usuarios con rol asignado
- Desactivar usuarios (soft delete)
- Endpoint: `GET/POST/DELETE /api/v1/users`

---

## 3. Multicompany (D12)

### 3.1. Concepto

La app soporta múltiples plantas/compañías del grupo Dupon, mapeando cada una a un `res.company` de Odoo. Cada request API incluye `company_id` para filtrar datos por tenant.

### 3.2. Compañías configuradas

| Short Code | Nombre | Odoo company_id |
|------------|--------|-----------------|
| IBE | Ibérica | 1 |
| GUD | Gudensberg | 2 |
| FRA | Francia | 3 |
| ITA | Italia | 4 |
| BEL | Bélgica | 5 |

### 3.3. Frontend — Selector de compañía

- **Ubicación**: Header del layout, junto al selector de idioma
- **Componente**: `CompanyContext` (React Context)
- **Visibilidad**: Solo se muestra si hay más de una compañía activa
- **Persistencia**: `localStorage` (`dcp-company-id`)
- **Datos**: Se cargan desde `GET /api/v1/auth/companies`

> **BUG-4 (activo)**: El selector de compañía ha desaparecido de la UI. El código existe en `layout.tsx` (líneas 165-179) y se renderiza condicionalmente cuando `companies.length > 1`. El problema puede ser que el endpoint `/auth/companies` no devuelve datos o la condición no se cumple.

---

## 4. Internacionalización (i18n)

### 4.1. Idiomas soportados (D15)

| Código | Idioma | Bandera |
|--------|--------|---------|
| `es` | Español | 🇪🇸 |
| `ca` | Catalán | — |
| `en` | English | 🇬🇧 |

### 4.2. Implementación

- **Archivo central**: `frontend/src/app/i18n/translations.ts` (~550 claves)
- **Provider**: `LanguageContext` → hook `useLanguage()` → función `t(key)`
- **Fallback**: Si falta una clave en el idioma actual, se muestra la versión en español
- **Persistencia**: `localStorage` (`dcp-language`)
- **Selector**: Dropdown en el header del layout (ES 🇪🇸 · CA · EN 🇬🇧)
- **Locales BCP-47**: `t("_locale")` devuelve `es-ES`, `ca-ES`, `en-GB` para formateo de fechas y números

### 4.3. Reglas i18n

- **Cero texto hardcodeado** en componentes — todo va por `t(key)`
- Las claves usan camelCase descriptivo: `dashAlertCritical`, `planColPODate`, `silosSyncBtn`
- Materiales traducidos con claves específicas: `matHarina`, `matAzucar`, `matAceite`

---

## 5. Dashboard (Página principal)

### 5.1. Barra de alertas

- Alerta roja (🔴) si algún silo está en estado **critical** (stock < safety stock)
- Alerta amarilla (⚠️) si algún silo está en estado **warning** (stock bajo)
- Se oculta automáticamente si todo está OK

### 5.2. Gauges de silos (estilo SCADA)

Por cada silo de la planta:
- **Barra vertical** con nivel de llenado (color-coded: verde/naranja/rojo)
- **Línea de safety stock** marcada en la barra
- **Porcentaje** con color dinámico según nivel
- **kg / capacidad** en formato legible (`18.5 t / 25.0 t`)
- **Próxima entrega** (📦 + fecha/hora relativa: "Hoy 14:30", "Mañana 08:00", "25/07")
- **Borde de tarjeta** color-coded según estado (verde/naranja/rojo)
- **Etiqueta de material** (Harina/Azúcar/Aceite) con color de énfasis

### 5.3. Gráfica de proyección de stock (Chart.js)

- **Tipo**: Línea temporal, forward-looking 14 días (configurable)
- **Datos**: Stock diario proyectado por silo (consumo - entregas PO)
- **Elementos visuales**:
  - Línea de stock con gradiente
  - Línea de safety stock horizontal
  - Línea de capacidad máxima horizontal
  - Eventos de PO marcados como puntos
- **Carga**: `GET /api/v1/silos/projection?company_id=X`

### 5.4. Tarjetas de estadísticas

4 stat cards en una fila:
- Silos OK (✅)
- Silos con stock bajo (⚠️)
- Silos críticos (🔴)
- Entregas pendientes (📦)

---

## 6. Silos — Vista detallada

### 6.1. Gauges por material

Los silos se agrupan por material (Harina, Azúcar, Aceite) con:
- Gauge grande (versión expandida del dashboard)
- Label del material con color de estado
- Stock actual vs capacidad

### 6.2. Delivery Timeline (Gantt horizontal)

Vista de timeline con las entregas planificadas:

| Componente | Detalle |
|-----------|---------|
| **Eje Y** | Silos (código + % llenado) |
| **Eje X** | Días del forecast (15/30/45 días, configurable) |
| **Hoy** | Columna resaltada |
| **PO pills** | Tarjetas compactas con nombre PO + cantidad |

#### Doble semáforo visual (v1.9)

Cada PO pill tiene **dos códigos de color independientes**:

1. **Fondo = Timing** (fecha PO vs fecha sugerida por la app):
   - 🟢 Verde: PO llega a tiempo (dentro de ±24h de la fecha sugerida)
   - 🟠 Naranja: PO llega tarde
   - 🔴 Rojo: Sin PO para este material

2. **Borde izquierdo = Confirmación proveedor**:
   - 🟢 Verde: `vendor_confirmed = true` (proveedor ha confirmado fecha)
   - 🔴 Rojo: `vendor_confirmed = false` (pendiente de confirmación)

#### Interacción

- **Pill clicable**: Si la PO es editable, al hacer clic se abre el modal de edición
- **Hover**: Escala + brillo (micro-animación, v1.9)
- **Tooltip**: Nombre PO + cantidad en kg

### 6.3. Filtros

- **Filtro por material**: Botones toggle para harina/azúcar/aceite
- **Forecast dropdown**: 15, 30 o 45 días de horizonte
- **Botón "Ver todo"**: Reset de filtros

### 6.4. Sync + Recálculo

- **Botón "Sincronizar"**: Fuerza sync Odoo → recálculo de entregas en cadena
- **Overlay animado**: Ring spinner con pasos ("Sincronizando con Odoo..." → "Recalculando entregas...")
- **Último sync**: Label relativo en el header ("🔄 15 min", "🔄 < 1 min")
- **Refresh post-sync**: Los datos se recargan automáticamente sin recargar la página (v1.7)

### 6.5. Modal de edición de fecha PO

- **Campos**:
  - Proveedor (chip 🏭, read-only)
  - Referencia materia prima (chip 📦, read-only, formato `[REF] Nombre`)
  - Fecha sugerida por la app (read-only, calculada)
  - Botón "↓ Usar propuesta" (copia la fecha sugerida al campo editable)
  - Fecha PO actual (editable, `datetime-local`)
- **Warning**: Si `vendor_confirmed = true`, se muestra aviso ⚠️
- **Bloqueo**: POs en estado `done` o `cancel` no son editables
- **Write-back**: `POST /api/v1/delivery-planning/update-date` → JSON-RPC a Odoo para actualizar `purchase.order.line.date_planned`
- **Diseño**: Gradient buttons, spring animation, +20% tamaño vs modal estándar (v1.9)

### 6.6. Delivery Planning Table (tabla complementaria)

Tabla detallada con todas las POs de materiales de silo:

| Columna | Contenido |
|---------|-----------|
| Material | Tipo de material |
| PO | Nombre de la PO |
| Proveedor | Nombre del proveedor |
| Producto | `[default_code] nombre` |
| Cantidad | kg |
| Fecha PO | Fecha planificada de Odoo |
| Fecha App | Fecha sugerida por la app |
| Estado | Estado Odoo (draft/purchase/done) |
| Semáforo | Doble color (timing + vendor) |

---

## 7. Panel de Configuración (IT only)

5 tabs accesibles solo para usuarios con rol `it`:

### 7.1. Tab "Líneas de producción"

- Lista de líneas (L01-L10) con capacidad teórica (kg/h)
- Edición inline de capacidad y estado activo/inactivo
- `GET/PUT /api/v1/config/lines`

### 7.2. Tab "Silos"

- Configuración de silos: código, nombre, material, capacidad, safety stock
- Edición inline de capacidad y safety stock
- `GET/PUT /api/v1/config/silos`

### 7.3. Tab "Usuarios"

- CRUD de usuarios con asignación de rol (`it` / `user`)
- Desactivación (no borrado físico)
- `GET/POST/DELETE /api/v1/users`

### 7.4. Tab "Recetas (kg/día)"

- Tabla CON completa: 14 formatos × 11 ingredientes
- Grid editable con valores en kg/día por máquina (24h)
- CRUD: crear nuevo formato/ingrediente, editar valor, eliminar
- `GET/POST/PUT/DELETE /api/v1/config/recipes`

**Ingredientes**: harina, azúcar, aceite, lecitina, sal, carbonato, caramelina, maltitol, cacao, colorante, oli_bany

**Formatos**: STD_R_110, STD_R_SS, HAAS_110, HAAS_98, HAAS_98_OREO, HAAS_110_OREO, MINI_75_SS, MINI_75_OLI, MINI_82, MINI_82_OREO, MINI_90, MINI_90_SS, IMPERIAL, BONCOLAC

### 7.5. Tab "Líneas ↔ Formatos"

- Mapping de qué formato puede ejecutar cada línea
- Número de máquinas por línea (8 para rotativos, 1 para lineales)
- Badge de tipo: `rotativa` vs `lineal`
- Edición de nº máquinas (bloqueo en hornos lineales, v1.7)
- `GET/PUT /api/v1/config/line-formats`

---

## 8. Sincronización con Odoo

### 8.1. Sync Engine

| Modelo Odoo | Tabla local | Qué sincroniza |
|-------------|------------|-----------------|
| `product.product` | `odoo_replica.products` | Productos RM y galleta |
| `mrp.workcenter` | `odoo_replica.workcenters` | Líneas de galleta (L01-L10) |
| `stock.quant` | `odoo_replica.stock_quants` | Niveles de inventario por silo |
| `mrp.production` | `odoo_replica.mrp_productions` | MOs activas/planificadas |
| `mrp.bom` + `mrp.bom.line` | `odoo_replica.mrp_boms/lines` | BOMs (referencia, no para cálculo) |
| `purchase.order` + `.line` | `odoo_replica.purchase_orders` | POs de RM con estado y proveedor |

### 8.2. Modos de operación

| Modo | Variable | Comportamiento |
|------|----------|----------------|
| **Real** | `ODOO_MODE=live` | Conecta a Odoo vía JSON-RPC |
| **Mock** | `ODOO_MODE=mock` | Salta el sync, usa datos locales |

### 8.3. Filtrado inteligente de stock_quants

- Lee los `odoo_location_id` configurados en `silo_configs`
- Solo trae quants de ubicaciones de silo (no de almacén general)
- Fallback a todas las ubicaciones internas si no hay configuración

### 8.4. Sync periódico

- Background worker asíncrono (`sync_worker.py`)
- Intervalo configurable vía `SYNC_INTERVAL_SECONDS` (default: 900 = 15 min)
- Tras cada sync, ejecuta `correction_engine.run()` para auto-calibrar factores

### 8.5. Sync manual (IT only)

- `POST /api/v1/sync/run` → ejecuta sync completo + recálculo
- `GET /api/v1/sync/status` → último estado del sync
- `GET /api/v1/sync/last` → timestamp del último sync (para label en UI)

---

## 9. Motor de Cálculo de Entregas

### 9.1. Flujo de cálculo

```
Por cada silo:
  1. stock_kg = stock_quant de Odoo (filtrado por location_id)
  2. consumption_kg_h = Σ (kg_per_day × machines / 24) por cada línea/formato
  3. consumption_corregido = consumption_kg_h × correction_factor
  4. hours_until_safety = (stock - safety_stock) / consumption_corregido - 4h margen
  5. suggested_dt = now + hours_until_safety
  6. qty_to_order = capacity - stock_proyectado_en_fecha_sugerida
```

### 9.2. Reglas de negocio

- **Entregas confirmadas no se recalculan** (D10): status `confirmed` → intocable
- **Recálculo bajo demanda** (D9): botón manual, no automático
- **Safety margin**: 4 horas antes del safety stock como buffer
- **PO matching**: Busca PO existente en Odoo con fecha ±3 días de la sugerida

### 9.3. Tabla CON como SSoT de consumos (D11)

Los consumos teóricos provienen del Excel CON (`Apro-PM 2026.ods`), **no de las BOMs de Odoo** (las BOMs de rotativos no son fiables).

Unidad: **kg consumidos por 1 máquina en 24h de producción continua**
- Rotativos (L01/L02/L06): 1 máquina = 1 horno rotativo → 8 máquinas por línea
- Lineales (HAAS/Mini): 1 máquina = 1 línea completa → 1 máquina

---

## 10. Factor de Corrección Auto-calibrado

### 10.1. Concepto

El factor compensa la desviación entre consumo teórico y real, que incluye:
- Merma de arranque
- Paros parciales
- Variaciones de receta
- Ajustes de sala de pasta (ya registrados en Odoo)

### 10.2. Cálculo (diario, post-sync)

```
stock_expected   = stock_ayer + entradas_hoy - consumo_teórico
stock_actual     = stock.quant de Odoo
consumo_real     = stock_ayer + entradas_hoy - stock_actual
factor           = consumo_real / consumo_teórico
```

### 10.3. Invariantes

- Rango válido: `[0.50, 2.00]` — fuera de rango → usa `1.0`
- Factor > 1.0: se consumió MÁS de lo esperado
- Factor < 1.0: se consumió MENOS
- Source: `auto` (calculado) o `seeded` (valor inicial del Excel)

### 10.4. Endpoints

- `GET /api/v1/corrections` — Histórico (últimos N días, filtrable por material)
- `GET /api/v1/corrections/current` — Factor activo por material (para dashboard)

---

## 11. Escritura a Odoo (limitada)

### 11.1. Scope de escritura (D17)

| Campo | Modelo Odoo | Condición |
|-------|-------------|-----------|
| `date_planned` | `purchase.order.line` | Único campo que la app escribe |

> **Nota:** La UI muestra el botón de edición a todos los usuarios autenticados.
> La restricción `role=it` se aplica en el backend (`require_role("it")`).
> Un usuario con rol `user` que intente editar recibirá HTTP 403.

### 11.2. Restricciones por estado

| Estado PO | Editable | Comportamiento |
|-----------|----------|----------------|
| `draft` | ✅ Sí | Edición libre |
| `sent` | ✅ Sí | Edición libre |
| `purchase` | ⚠️ Con warning | Si `vendor_confirmed`, muestra aviso |
| `done` | ❌ No | Bloqueado en UI y API |
| `cancel` | ❌ No | Bloqueado en UI y API |

---

## 12. Logging y Administración

### 12.1. Logging profesional

- `RotatingFileHandler` → `logs/dcp.log` (5 MB × 3 rotaciones)
- Logs estructurados con `extra={}` para trazabilidad
- Sin datos sensibles (PII limpia)

### 12.2. Endpoint de logs (IT only)

- `GET /api/v1/admin/logs` — Devuelve las últimas N líneas del log (role=it)

---

## 13. Deploy

### 13.1. Infraestructura

| Componente | Servicio | Notas |
|-----------|----------|-------|
| Backend | Cloud Run | Dockerfile multi-stage, non-root |
| Frontend | Cloud Run | Next.js standalone output |
| Base de datos | Cloud SQL (PostgreSQL) | Schemas: `odoo_replica` + `dcp_app` |
| Secretos | GCP Secret Manager | `.env` solo en desarrollo |

### 13.2. Stack local (Docker Compose)

```bash
docker-compose up  # PostgreSQL + Backend + Frontend
```

### 13.3. Migraciones

- Alembic (0001 → 0003), ejecutadas con `alembic upgrade head`
- Seed data incluido en las migraciones (silos Ibérica, tabla CON, line_formats)

---

## 14. Decisiones Arquitecturales Registradas

| ID | Decisión | Motivo |
|----|----------|--------|
| D1 | Odoo es SSoT | Evitar doble fuente de verdad |
| D2 | DCP = cache + cálculos | Simplicidad, no es un ERP |
| D9 | Recálculo manual (botón) | Flujo operativo: ajustar → recalcular → actuar |
| D10 | Entregas confirmadas = bloqueadas | Evitar recálculo sobre datos ya comprometidos |
| D11 | Consumos de Excel CON, no BOM Odoo | BOMs de rotativos no fiables |
| D12 | Multicompany | 5 compañías del grupo |
| D13 | Solo silos (no IBC/sacos) | Eso lo gestiona Odoo |
| D14 | Mock data activable | Validación de UI sin Odoo real |
| D15 | i18n: ES, CA, EN | 3 idiomas, sin texto hardcodeado |
| D16 | Solo materiales de silo en filtros UI | Harina, azúcar, aceite — no lecitina/sal/etc. |
| D17 | Write-back limitado a `date_planned` | Mínimo riesgo transaccional |

---

## 15. Features Planificadas (No implementadas)

### 15.1. Fase 6 — Plant Definition Files + Corrección por Peso

- **Archivos YAML por planta**: Definición inmutable de silos, líneas, formatos y capacidades. SSoT versionado en Git para evitar errores de agentes IA.
- **Flexibilidad de formatos**: Todas las líneas pueden hacer SS y Oreo (no solo las actualmente mapeadas). El mapping `line_formats` pasa a significar "qué puede hacer" en vez de "qué está haciendo".
- **Corrección por peso de galleta**: Factor proporcional al peso nominal del formato para ajustar consumo cuando cambia el gramaje.
- **Conexión MOs → consumo real** (TECH-9): En vez de asumir que todas las líneas producen simultáneamente, usar las MOs de Odoo para saber qué produce cada línea.

### 15.2. Backlog Técnico

| ID | Feature | Estado |
|----|---------|--------|
| TECH-8 | Gráfica de tendencia histórica de consumo por silo | Propuesta evaluada |
| TECH-10 | Unificar DeliveryPlanningTable + DeliveryTimeline | Evaluación pendiente |
| TECH-11 | Tests para `_compute_timing_color` y `_compute_editability` | Pendiente |
| TECH-12 | Migración Alembic para `partner_name` y `vendor_confirmed` (PG) | Pendiente |

### 15.3. Futuro (fuera de scope actual)

- **Aluminio** (troquelado, enrollado) — fase futura
- **Capacidad comercial (CTP)** — fase futura
- **Simulación What-If** — fase futura
- **Gestión de MOs/turnos** — siempre en Odoo, nunca en DCP
