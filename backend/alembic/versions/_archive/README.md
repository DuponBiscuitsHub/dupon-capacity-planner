# Migraciones Alembic Archivadas

Estas migraciones formaban una cadena paralela que fue reemplazada por
la cadena `0001_initial` → `0002_correction_factors` → `0003_kg_per_day`.

## Archivadas

1. **`192025bdaf66_initial_schema.py`** (2026-05-27)
   - Primera versión del schema. Reemplazada por `0001_initial` que incluye
     schemas PostgreSQL (`odoo_replica`, `dcp_app`) y todas las tablas.

2. **`b21025bdaf67_add_historical_ml_tables.py`** (2026-06-04)
   - Tablas ML/histórico para fase futura: `silo_consumption_history`,
     `aluminum_operations_history`, `oven_throughput_history`.
   - Dependía de `192025bdaf66`. No tiene equivalente en la cadena actual.
   - Cuando se necesiten estas tablas, crear una nueva migración `0004+`.

## Por qué archivar en vez de eliminar

Valor histórico: documentan decisiones de diseño temprano.
Se movieron aquí en vez de borrarse por política del proyecto
(ver AGENTS.md: "No eliminar docs sin mover a archive").
