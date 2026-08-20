# Coding Standards — DCP Raw Material Planner
> **Versión 1.0 · 06/07/2026**
>
> Adoptado de `odoo-label_edge/docs/coding_standards.md`.
> Todo agente o developer que toque este repo debe leerlo antes de escribir código.

---

## 1. Principios fundamentales (en orden de precedencia)

| # | Principio | Qué significa en práctica |
|---|-----------|--------------------------| 
| 1 | **Seguridad** | Validar todo input en los límites. Sin secretos hardcoded. Sin datos sensibles en logs |
| 2 | **Correctitud** | Sin bugs. Si hay duda, añade un test |
| 3 | **Legibilidad** | Un developer junior entiende el flujo principal en 2 minutos |
| 4 | **Mantenibilidad** | SOLID, SSoT, sin duplicidad |
| 5 | **Elegancia** | Consistencia estricta en naming. Funciones pequeñas |
| 6 | **Rendimiento** | Solo cuando sea un problema real y medido |

---

## 2. Naming conventions

### Python (backend)

```python
# Módulos y ficheros → snake_case.py
delivery_calculator.py, sync_worker.py     ✅
DeliveryCalculator.py                      ❌

# Clases → PascalCase
class SyncWorker:                          ✅
class sync_worker:                         ❌

# Funciones y métodos → snake_case
def recalculate_deliveries():              ✅
def recalculateDeliveries():               ❌

# Variables y parámetros → snake_case
silo_stock, company_id, capacity_kg_h     ✅
siloStock, companyId                       ❌

# Constantes → UPPER_SNAKE_CASE
SYNC_INTERVAL_SECONDS = 900
SAFETY_MARGIN_HOURS = 4
```

### TypeScript / JavaScript (frontend)

```typescript
// Variables y funciones → camelCase
const siloStock = 18200;
function handleRecalculate() {}

// Constantes → UPPER_SNAKE_CASE
const MAX_SILOS = 5;

// Componentes React → PascalCase
function SiloCard() {}

// CSS Modules → camelCase (className)
styles.siloCard, styles.deliveryRow         ✅
styles['silo-card']                         ❌

// Interfaces/Types → PascalCase
interface DeliverySuggestion {}
type SiloStatus = 'ok' | 'warning' | 'critical';
```

### HTML / CSS

```css
/* IDs de elementos: kebab-case */
#btn-recalculate, #silo-panel

/* CSS classes en modules: camelCase */
.siloCard, .deliveryTable
```

---

## 3. Estructura de ficheros

### Backend

```
backend/app/
├── main.py              ← Solo: startup, lifespan, routers. Sin lógica
├── core/
│   ├── config.py        ← Solo: Settings (Pydantic). Sin defaults de negocio
│   ├── database.py      ← Solo: engine, SessionLocal, get_db
│   ├── security.py      ← JWT, bcrypt, require_auth, require_role
│   ├── odoo_client.py   ← JSON-RPC client. OOP (tiene estado: uid, sesión)
│   └── sync_engine.py   ← Orquestador sync. OOP (tiene estado: db session)
├── models/              ← SQLAlchemy ORM. Sin lógica de negocio
├── routers/             ← FastAPI routers. Solo HTTP: recibe, valida, delega, devuelve
├── services/            ← Lógica de negocio. Sin HTTP, sin SQLAlchemy directo
└── tests/
```

**Regla de capas:** Router → Service → Model. Los routers NO tocan la BD directamente.

### Frontend

```
frontend/src/app/
├── (dashboard)/
│   ├── layout.tsx       ← Sidebar + Header. Verificación de sesión
│   ├── page.tsx         ← Dashboard resumen
│   ├── silos/page.tsx   ← Panel SCADA, entregas, recalcular
│   └── config/page.tsx  ← Config (IT panel)
├── login/page.tsx       ← Login contra backend
├── context/             ← React contexts (Company, Language)
├── i18n/                ← Traducciones ES + EN
└── utils/               ← Helpers puros
```

---

## 4. Funciones y métodos

- **Máximo 40 líneas** por función. Si supera, extraer sub-funciones.
- Una función = una responsabilidad. El nombre dice qué hace.
- Máximo **5 parámetros**. Si hay más, usar dataclass o Pydantic schema.
- **Type hints siempre**: parámetros y valor de retorno (Python). TypeScript strict.

```python
# ✅ Nombre claro, responsabilidad única, type hints
def calculate_silo_autonomy(
    current_stock_kg: float,
    consumption_kg_h: float,
    safety_stock_kg: float,
) -> float:
    """Retorna horas de autonomía hasta safety stock."""
    ...

# ❌ Hace demasiado, sin tipos
def handle_silo_stuff(data):
    ...
```

---

## 5. Paradigma de código

> **Clase solo si el objeto tiene estado propio entre llamadas. Sin estado → función.**

| Capa | Paradigma | Razón |
|------|-----------|-------|
| `models/` | OOP | SQLAlchemy lo exige |
| `routers/` | Funcional | Idiomático en FastAPI |
| `services/delivery_calculator` | Funcional | `recalculate(db, company_id) → list`. Sin estado |
| `services/sync_worker` | OOP | Tiene estado: `is_running`, `_task` |
| `core/odoo_client` | OOP | Tiene estado: `uid`, sesión HTTP |
| `core/config` | OOP (Pydantic) | Lo exige Pydantic |

---

## 6. Comentarios y docstrings

Comentar el **POR QUÉ**, no el qué:

```python
# ✅ Explica la decisión
# No recalcular entregas confirmadas: el planificador ya negoció
# la fecha con el proveedor y creó la PO en Odoo.
if suggestion.status == "confirmed":
    continue

# ❌ Obvio
# Incrementar el stock
stock += qty
```

Docstrings solo en funciones públicas de servicios:

```python
def recalculate_deliveries(db: Session, company_id: int) -> list[dict]:
    """Recalcula sugerencias de entrega para silos de una planta.

    Solo toca entregas con status != 'confirmed' (las confirmadas están bloqueadas).
    Lee stock actual, MOs activas, BOM y capacidad por línea para proyectar consumo.

    Returns:
        Lista de sugerencias con fecha, hora, cantidad y estado PO.
    """
```

---

## 7. Manejo de errores

### Nunca silenciar

```python
# ❌ PROHIBIDO
try:
    sync_stock_quants()
except Exception:
    pass

# ✅ Con contexto
try:
    sync_stock_quants()
except Exception as e:
    logger.error("Failed to sync stock_quants", extra={
        "company_id": company_id,
        "error": str(e),
    })
    raise
```

### Sin datos sensibles en logs

```python
# ❌ NUNCA
logger.debug(f"Odoo API key: {settings.ODOO_API_KEY}")

# ✅
logger.debug(f"Odoo auth: {'configured' if settings.ODOO_API_KEY else 'MISSING'}")
```

---

## 8. Seguridad en código

- **Secretos**: solo en `.env` (dev) o GCP Secret Manager (prod). Nunca en código.
- **Validación**: toda entrada externa se valida en el router (Pydantic), no en el interior.
- **SQL**: siempre SQLAlchemy ORM, nunca concatenación de strings.
- **Auth**: todo endpoint protegido con `require_auth()`. Endpoints IT con `require_role("it")`.
- **Cookies**: `HttpOnly; Secure; SameSite=Strict`. Nunca `document.cookie` en frontend.

---

## 9. Tests

### Cuándo
- Toda función de servicio con lógica no trivial → test unitario.
- Todo endpoint de auth → test de seguridad.
- Motor de cálculo → tests con datos conocidos.

### Estructura
```
backend/app/tests/
├── test_delivery_calculator.py
├── test_auth.py
├── test_sync_engine.py
└── test_api_silos.py
```

---

## 10. Definition of Done

Una tarea está **terminada** solo si:

1. ✅ Cumple los criterios de aceptación de su fase
2. ✅ No introduce regresiones conocidas
3. ✅ El código sigue estos estándares
4. ✅ Los casos de error relevantes están contemplados
5. ✅ Tests añadidos o ausencia justificada
6. ✅ Sin secretos en código o logs
7. ✅ `proyecto_maestro.md` actualizado (tarea marcada ✅)
8. ✅ `.env.example` actualizado si se añadió variable nueva
