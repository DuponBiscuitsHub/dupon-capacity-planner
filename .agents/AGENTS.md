# DCP Raw Material Planner — Reglas para Agentes IA

## Scope del Proyecto

Este proyecto es una aplicación web (FastAPI + Next.js + PostgreSQL) que planifica
las entregas de primera materia de galleta para Dupon. Odoo es SSoT absoluto.
Este servicio solo cachea lo mínimo para calcular ventanas de descarga de camiones
cisterna y mostrar el estado de los silos de producción.

**Gestiona:**
- Estado de silos de primera materia (harina, azúcar, aceite de coco)
- Cálculo de fecha+hora óptima de descarga de camiones
- Visibilidad de POs existentes y su estado de confirmación
- Planificación de entregas con semáforo (green/orange/red) y write-back de `date_planned` a Odoo
- Capacidad teórica por línea de producción (configurable)

**NO gestiona:**
- Aluminio (troquelado, enrollado) — fase futura
- Capacidad comercial (CTP) — fase futura
- Simulación What-If — fase futura
- Escritura en Odoo **excepto** `purchase.order.line.date_planned` (todo lo demás es read-only)
- Gestión de MOs ni turnos (eso es Odoo)

**Arquitectura:**
Backend FastAPI + PostgreSQL (Cloud SQL). Frontend Next.js. Deploy en Cloud Run.
Sync periódico cada 15 min vía JSON-RPC contra Odoo.

## Estado y Progreso

1. **`docs/proyecto_maestro.md`** es la fuente única de verdad del estado del proyecto.
   - Antes de empezar cualquier tarea, leerlo.
   - Después de completar una tarea, actualizar el checkbox correspondiente.
   - Si una tarea cambia de scope, actualizar la descripción ANTES de tocar código.

2. **No asumir que el proyecto está en un estado diferente al documentado.**
   Si un doc dice que algo no está implementado, verificar en el código antes de actuar.

## Restricciones de Código

1. **Solo primera materia galleta.** No añadir lógica de aluminio, comercial ni simulación.
2. **Odoo es SSoT.** No implementar gestión de MOs, turnos ni estados de producción.
3. **Sin abstracciones prematuras.** Si solo hay 1 tipo de cálculo, no crear un factory pattern.
4. **Python: snake_case. JS/TS: camelCase.** Ver `docs/coding_standards.md` para detalle.
5. **Funcional por defecto.** Clases solo si el objeto tiene estado propio entre llamadas.
6. **Type hints siempre** en Python (parámetros y return). TypeScript strict en frontend.
7. **Máximo 40 líneas** por función. Si supera, extraer sub-funciones.
8. **Comentar el POR QUÉ, no el QUÉ.** El código explica el qué.
9. **2 roles de auth:** `it` (admin) y `user`. Todo endpoint protegido.
10. **i18n:** ES, CA y EN. Claves en `translations.ts`. Sin texto hardcodeado.

## Documentación

1. **Antes de una reestructuración:** actualizar docs primero, código después.
2. **Después de completar una fase:** actualizar `proyecto_maestro.md` (checkboxes).
3. **No eliminar docs sin mover a `docs/archive/`** si tienen valor histórico.

## Convención de Commits

Formato: `tipo(scope): descripción`

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `deploy`
Scopes: `auth`, `silos`, `sync`, `config`, `frontend`, `models`, `api`, `deploy`

Ejemplos:
- `feat(silos): implement delivery recalculation endpoint`
- `docs(maestro): update phase 1 checkboxes`
- `fix(sync): handle Odoo timeout in stock_quants pull`
- `feat(auth): implement JWT login with HttpOnly cookie`

## Archivos Críticos (no modificar sin contexto)

| Archivo | Motivo |
|---------|--------|
| `docs/proyecto_maestro.md` | SSoT del proyecto. Leer antes de cualquier tarea |
| `docs/features.md` | Guía de funcionalidades. Verificar antes de eliminar código |
| `docs/coding_standards.md` | Estándares de código. Seguir siempre |
| `.env.example` | Template de configuración. Actualizar si se añade variable |
| `backend/scripts/seed_config.py` | **SSoT de config de fábrica.** Silos, líneas, recetas CON, formatos. No modificar datos sin confirmar con usuario |
| `backend/app/core/odoo_client.py` | Cliente JSON-RPC probado. No reescribir sin motivo |
| `backend/app/core/sync_engine.py` | Motor de sync. Adaptar, no reescribir |

## Entorno de Desarrollo

### Venv del proyecto
```
/home/pakipy/dupon-dev/dupon-capacity-planner/.venv/
```
El venv está en la **raíz del mono-repo** (no dentro de `backend/`).
Siempre usar `.venv/bin/python3` y `.venv/bin/pip`.

### ⚠️ Problema conocido: terminal cuelga al importar módulos Python
**Causa:** `backend/.env` apunta a PostgreSQL. `config.py` carga el `.env` al
importar, y SQLAlchemy intenta conectar al pool → cuelga si no hay servidor.

**Solución — arrancar backend en modo mock:**
```bash
cd backend
env -i DATABASE_URL="sqlite:///./dev.db" JWT_SECRET="secreto32charsminimo" \
  ODOO_MODE=mock APP_ENV=development \
  ../.venv/bin/uvicorn app.main:app --reload --port 8000
```

**Solución — correr tests:**
```bash
cd backend
env -i DATABASE_URL="sqlite:///:memory:" JWT_SECRET="test_secret_32chars_ok" \
  ODOO_MODE=mock ../.venv/bin/pytest app/tests/ -v
```

> `env -i` limpia el entorno del shell, evitando que variables heredadas
> interfieran. Alternativa: crear `backend/.env.test` con valores seguros.

## Deploy y Mantenimiento

- **Rama de trabajo: `Beta`** — todo el desarrollo se hace aquí.
- **Flujo:** commit en `Beta` → PR/merge a `main` cuando la fase esté completa.
- **Deploy:** Cloud Run (backend + frontend). Cloud SQL (PostgreSQL).
- **Secretos:** GCP Secret Manager en producción. `.env` local en desarrollo.

## Pendientes sin resolver (TBD)

| ID | Pregunta | Estado |
|----|----------|--------|
| TBD-1 | ¿Qué modelo Odoo usan para ajustes diarios de la sala de pasta? | Pendiente |
| TBD-2 | ¿Cuántas líneas tiene Gudensberg? | Pendiente (~5, confirmar) |
| TBD-3 | ¿Qué location_id de Odoo corresponde a cada silo en Ibérica? | ✅ Resuelto — Silo1=79, Silo2=80, Silo3=81, Azúcar=82, Aceite=83 |
| TBD-4 | ¿Qué product_id de Odoo son harina, azúcar y aceite de coco? | ✅ Resuelto — Harina=49486, Azúcar=49488, Aceite=49492 |
| TBD-5 | ¿Qué workcenter_id de Odoo son L01-L10? | Pendiente |
