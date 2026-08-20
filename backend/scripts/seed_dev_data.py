"""
seed_dev_data.py — Datos de muestra para desarrollo local.

Inserta en SQLite:
- Silos Ibérica (S-H1/H2/H3, S-AZ, S-AC, S-LC, S-SA, S-CA, S-ML)
- Líneas L01-L10 con consumos teóricos
- Productos Odoo (harina, azúcar, aceite)
- Work centers L01-L10
- Stock actual simulado (quants)
- 3 Purchase Orders de ejemplo
- Tabla CON completa (format_code × material_type → kg_per_day)
- Line formats (línea → formato con nº máquinas)
- Usuarios de desarrollo

Idempotente: limpia y reinserta en cada ejecución.
Uso:
  cd /ruta/al/proyecto
  .venv/bin/python3 seed_dev_data.py
"""
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_PROJECT_ROOT, "backend", "dev.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")
os.environ.setdefault("JWT_SECRET", "secreto_dev_32chars_minimo_ok_ok")
os.environ.setdefault("ODOO_MODE", "mock")
os.environ.setdefault("APP_ENV", "development")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.database import _IS_SQLITE, _sqlite_init, SessionLocal  # noqa: E402
from app.models.planner import (  # noqa: E402
    Company, SiloConfig, LineCapacity, RefConsumptionRate, LineFormat,
)
from app.models.odoo_replica import (  # noqa: E402
    StockQuant, Product, Workcenter, PurchaseOrder,
)
from sqlalchemy import text  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

if _IS_SQLITE:
    _sqlite_init()

db = SessionLocal()

# ── Limpiar tablas (preservar users) ──────────────────────────────────────────
for tbl in [
    "delivery_suggestions", "correction_factors",
    "stock_quants", "purchase_orders",
    "mrp_productions", "mrp_bom_lines", "mrp_boms",
    "workcenters", "products",
    "line_capacities", "line_formats", "product_format_mappings",
    "ref_consumption_rates", "silo_configs",
]:
    try:
        db.execute(text(f"DELETE FROM {tbl}"))
    except Exception:
        pass  # Tabla puede no existir en SQLite sin schema
db.commit()
print("🗑️  Tablas limpiadas")

# ── Compañías ─────────────────────────────────────────────────────────────────
companies = [
    Company(id=1, name="Galletas Dupon Ibérica", odoo_company_id=1, short_code="IBE"),
    Company(id=2, name="Galletas Dupon Gudensberg", odoo_company_id=2, short_code="GUD"),
    Company(id=3, name="Biscuits Dupon France", odoo_company_id=3, short_code="FRA"),
    Company(id=4, name="Biscotti Dupon Italia", odoo_company_id=4, short_code="ITA"),
    Company(id=5, name="Biscuits Dupon Belgium", odoo_company_id=5, short_code="BEL"),
]
# Limpiar y reinsertar (merge para evitar conflictos de PK)
for c in companies:
    existing = db.query(Company).filter(Company.id == c.id).first()
    if existing:
        existing.name = c.name
        existing.odoo_company_id = c.odoo_company_id
        existing.short_code = c.short_code
    else:
        db.add(c)
db.commit()
print(f"✅ Compañías: {len(companies)}")

# ── Productos Odoo (harina, azúcar, aceite) ──────────────────────────────────
# IDs confirmados en staging3 (dupon-staging3.processcontrol.sh)
products = [
    Product(odoo_id=49486, name="Harina Baking Granel",
            default_code="A00/00010", uom_id=1, company_id=1),
    Product(odoo_id=49488, name="Azucar Granel",
            default_code="A00/00020", uom_id=1, company_id=1),
    Product(odoo_id=49492, name="Aceite Coco Refinado",
            default_code="A00/00041", uom_id=1, company_id=1),
]
db.add_all(products)
db.commit()
print(f"✅ Productos: {len(products)}")

# ── Work centers L01-L10 ─────────────────────────────────────────────────────
workcenters = [
    Workcenter(odoo_id=i, name=f"Línea {i:02d}", code=f"L{i:02d}", company_id=1)
    for i in range(1, 11)
]
db.add_all(workcenters)
db.commit()
print(f"✅ Work centers: {len(workcenters)}")

# ── Silos Ibérica ─────────────────────────────────────────────────────────────
# odoo_location_id confirmados en staging3
silos = [
    SiloConfig(silo_code="S-H1", name="Silo Harina 1",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=79),
    SiloConfig(silo_code="S-H2", name="Silo Harina 2",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=80),
    SiloConfig(silo_code="S-H3", name="Silo Harina 3",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=81),
    SiloConfig(silo_code="S-AZ", name="Silo Azúcar",
               material_type="azucar", capacity_kg=30000, safety_stock_kg=2500,
               company_id=1, odoo_location_id=82),
    SiloConfig(silo_code="S-AC", name="Silo Aceite Coco",
               material_type="aceite", capacity_kg=20000, safety_stock_kg=1500,
               company_id=1, odoo_location_id=83),
]
db.add_all(silos)
db.commit()
print(f"✅ Silos: {len(silos)}")

# ── Stock actual simulado ─────────────────────────────────────────────────────
silo_ids = {s.silo_code: s.id for s in db.query(SiloConfig).all()}
now = datetime.now(timezone.utc)

quants = [
    StockQuant(odoo_id=201, product_id=101, location_id=silo_ids["S-H1"],
               quantity=18500.0, reserved_quantity=0.0, company_id=1),
    StockQuant(odoo_id=202, product_id=101, location_id=silo_ids["S-H2"],
               quantity=12300.0, reserved_quantity=0.0, company_id=1),
    StockQuant(odoo_id=203, product_id=101, location_id=silo_ids["S-H3"],
               quantity=3200.0, reserved_quantity=0.0, company_id=1),    # ⚠ bajo
    StockQuant(odoo_id=204, product_id=102, location_id=silo_ids["S-AZ"],
               quantity=16500.0, reserved_quantity=0.0, company_id=1),
    StockQuant(odoo_id=205, product_id=103, location_id=silo_ids["S-AC"],
               quantity=2800.0, reserved_quantity=0.0, company_id=1),    # 🔴 crítico
]
db.add_all(quants)
db.commit()
print(f"✅ Stock quants: {len(quants)}")

# ── Líneas de producción ──────────────────────────────────────────────────────
line_data = [
    ("L01", 450), ("L02", 450), ("L03", 380),
    ("L04", 380), ("L05", 320), ("L06", 320),
    ("L07", 280), ("L08", 280), ("L09", 250),
    ("L10", 250),
]
lines = [
    LineCapacity(line_code=code, capacity_kg_h=kg_h, company_id=1)
    for code, kg_h in line_data
]
db.add_all(lines)
db.commit()
print(f"✅ Líneas: {len(lines)}")

# ── Purchase Orders ───────────────────────────────────────────────────────────
tomorrow = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
day3 = (now + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0)
day6 = (now + timedelta(days=6)).replace(hour=8, minute=0, second=0, microsecond=0)

pos = [
    PurchaseOrder(odoo_id=1001, name="PO/2026/0142",
                  product_id=101, quantity=22000.0,
                  date_planned=tomorrow, state="purchase", company_id=1),
    PurchaseOrder(odoo_id=1002, name="PO/2026/0143",
                  product_id=101, quantity=22000.0,
                  date_planned=day6, state="draft", company_id=1),
    PurchaseOrder(odoo_id=1003, name="PO/2026/0144",
                  product_id=102, quantity=18000.0,
                  date_planned=day3, state="purchase", company_id=1),
]
db.add_all(pos)
db.commit()
print(f"✅ Purchase Orders: {len(pos)}")

# ── Tabla CON — consumos de referencia (kg/día por 1 máquina, 24h) ────────────
# Fuente: hoja CON del Excel Apro-PM 2026.ods (Ibérica, company_id=1)
# format_code × material_type → kg_per_day
CON_DATA = [
    # (format_code,      material_type, kg_per_day)
    # ── HARINA ─────────────────────────────────────────────────────────────
    ("STD_R_110",    "harina",    447),
    ("STD_R_SS",     "harina",    467),
    ("HAAS_110",     "harina",   3501),
    ("HAAS_98",      "harina",   3105),
    ("HAAS_98_OREO", "harina",   3105),
    ("HAAS_110_OREO","harina",   3501),
    ("MINI_75_SS",   "harina",    241),
    ("MINI_75_OLI",  "harina",    224),
    ("MINI_90_SS",   "harina",    377),
    ("MINI_90",      "harina",    350),
    ("IMPERIAL",     "harina",    473),
    ("MINI_82",      "harina",    303),
    ("MINI_82_OREO", "harina",    269),
    ("BONCOLAC",     "harina",    447),
    # ── AZÚCAR ─────────────────────────────────────────────────────────────
    ("STD_R_110",    "azucar",    205),
    ("STD_R_SS",     "azucar",      0),
    ("HAAS_110",     "azucar",   1587),
    ("HAAS_98",      "azucar",   1408),
    ("HAAS_98_OREO", "azucar",   1408),
    ("HAAS_110_OREO","azucar",   1587),
    ("MINI_75_SS",   "azucar",      0),
    ("MINI_75_OLI",  "azucar",    103),
    ("MINI_90_SS",   "azucar",      0),
    ("MINI_90",      "azucar",    161),
    ("IMPERIAL",     "azucar",    218),
    ("MINI_82",      "azucar",    140),
    ("MINI_82_OREO", "azucar",    135),
    ("BONCOLAC",     "azucar",    205),
    # ── ACEITE COCO ────────────────────────────────────────────────────────
    ("STD_R_110",    "aceite",     22),
    ("STD_R_SS",     "aceite",     25),
    ("HAAS_110",     "aceite",    185),
    ("HAAS_98",      "aceite",    164),
    ("HAAS_98_OREO", "aceite",    164),
    ("HAAS_110_OREO","aceite",    185),
    ("MINI_75_SS",   "aceite",     13),
    ("MINI_75_OLI",  "aceite",     38),
    ("MINI_90_SS",   "aceite",     20),
    ("MINI_90",      "aceite",     17),
    ("IMPERIAL",     "aceite",     24),
    ("MINI_82",      "aceite",     15),
    ("MINI_82_OREO", "aceite",     17),
    ("BONCOLAC",     "aceite",     22),
    # ── LECITINA ───────────────────────────────────────────────────────────
    ("STD_R_110",    "lecitina",   10),
    ("STD_R_SS",     "lecitina",   11),
    ("HAAS_110",     "lecitina",   79),
    ("HAAS_98",      "lecitina",   70),
    ("HAAS_98_OREO", "lecitina",   70),
    ("HAAS_110_OREO","lecitina",   79),
    ("MINI_75_SS",   "lecitina",    6),
    ("MINI_75_OLI",  "lecitina",    5),
    ("MINI_90_SS",   "lecitina",    9),
    ("MINI_90",      "lecitina",    7),
    ("IMPERIAL",     "lecitina",   10),
    ("MINI_82",      "lecitina",    6),
    ("MINI_82_OREO", "lecitina",    7),
    ("BONCOLAC",     "lecitina",   10),
    # ── SAL ────────────────────────────────────────────────────────────────
    ("STD_R_110",    "sal",         4),
    ("STD_R_SS",     "sal",         4),
    ("HAAS_110",     "sal",        30),
    ("HAAS_98",      "sal",        26),
    ("HAAS_98_OREO", "sal",        26),
    ("HAAS_110_OREO","sal",        30),
    ("MINI_75_SS",   "sal",         2),
    ("MINI_75_OLI",  "sal",         2),
    ("MINI_90_SS",   "sal",         3),
    ("MINI_90",      "sal",         3),
    ("IMPERIAL",     "sal",         4),
    ("MINI_82",      "sal",         3),
    ("MINI_82_OREO", "sal",         3),
    ("BONCOLAC",     "sal",         4),
    # ── CARBONAT ───────────────────────────────────────────────────────────
    ("HAAS_110",     "carbonat",   12),
    ("HAAS_98",      "carbonat",   11),
    ("HAAS_98_OREO", "carbonat",   11),
    ("HAAS_110_OREO","carbonat",   12),
    # ── CARAMELINA ─────────────────────────────────────────────────────────
    ("HAAS_110",     "caramelina", 12),
    ("HAAS_98",      "caramelina", 10),
    # ── MALTITOL (solo formatos sin azúcar) ────────────────────────────────
    ("STD_R_SS",     "maltitol",  300),
    ("MINI_75_SS",   "maltitol",  147),
    ("MINI_90_SS",   "maltitol",  300),
    # ── CACAO (solo oreo) ──────────────────────────────────────────────────
    ("MINI_82_OREO", "cacao",      32),
    ("HAAS_98_OREO", "cacao",      32),
    ("HAAS_110_OREO","cacao",      32),
    # ── COLORANTE (solo oreo) ──────────────────────────────────────────────
    ("MINI_82_OREO", "colorante",   4),
    ("HAAS_98_OREO", "colorante",   4),
    ("HAAS_110_OREO","colorante",   4),
    # ── OLI BANY (aceite de baño, solo Mini 75 oli) ────────────────────────
    ("MINI_75_OLI",  "oli_bany",  165),
]

con_rows = [
    RefConsumptionRate(format_code=fc, material_type=mt, kg_per_day=kg, company_id=1)
    for fc, mt, kg in CON_DATA
]
db.add_all(con_rows)
db.commit()
print(f"✅ Tabla CON (ref_consumption_rates): {len(con_rows)} filas")

# ── Line Formats (línea → formato con nº máquinas) ───────────────────────────
LF_DATA = [
    # (line_code, format_code, machines)
    # Rotativos (8 hornos)
    ("L01_L02", "STD_R_110", 8),
    ("L01_L02", "STD_R_SS",  8),
    ("L06",     "STD_R_110", 8),
    ("L06",     "STD_R_SS",  8),
    # Lineales HAAS
    ("L03", "HAAS_110",      1),
    ("L03", "HAAS_110_OREO", 1),
    ("L04", "HAAS_110",      1),
    ("L04", "HAAS_98",       1),
    ("L04", "HAAS_98_OREO",  1),
    ("L04", "HAAS_110_OREO", 1),
    ("L07", "HAAS_110",      1),
    ("L09", "HAAS_98",       1),
    ("L09", "HAAS_98_OREO",  1),
    ("L10", "HAAS_98",       1),
    ("L10", "HAAS_98_OREO",  1),
    # Lineales Mini
    ("L05", "MINI_75_SS",    1),
    ("L05", "MINI_75_OLI",   1),
    ("L05", "MINI_82",       1),
    ("L08", "MINI_82",       1),
    ("L08", "MINI_82_OREO",  1),
]

lf_rows = [
    LineFormat(line_code=lc, format_code=fc, machines=m, company_id=1)
    for lc, fc, m in LF_DATA
]
db.add_all(lf_rows)
db.commit()
print(f"✅ Line formats: {len(lf_rows)}")

db.close()

# ── Usuarios de desarrollo ────────────────────────────────────────────────────
from app.models.planner import User  # noqa: E402
from app.core.security import hash_password  # noqa: E402

_DEV_USERS = [
    {"username": "it_admin", "password": "DuponIT2026",    "role": "it"},
    {"username": "admin",    "password": "DuponAdmin2026", "role": "it"},
]
db2 = SessionLocal()
for u_data in _DEV_USERS:
    u = db2.query(User).filter_by(username=u_data["username"]).first()
    if u:
        u.hashed_password = hash_password(u_data["password"])
        u.default_company_id = 1
        print(f"✅ Usuario '{u_data['username']}' actualizado")
    else:
        db2.add(User(
            username=u_data["username"],
            hashed_password=hash_password(u_data["password"]),
            role=u_data["role"],
            is_active=True,
            default_company_id=1,
        ))
        print(f"✅ Usuario '{u_data['username']}' creado")
db2.commit()
db2.close()

print("")
print("🎉 Seed completado:")
print("   S-H1 → 18.500 kg harina  (74%)")
print("   S-H2 → 12.300 kg harina  (49%)")
print("   S-H3 →  3.200 kg harina  (13%) ⚠️")
print("   S-AZ → 16.500 kg azúcar  (55%)")
print("   S-AC →  2.800 kg aceite  (14%) 🔴")
print("   POs  → PO142 harina mañana, PO144 azúcar en 3 días")
print("   Login: admin / DuponAdmin2026  |  it_admin / DuponIT2026")
