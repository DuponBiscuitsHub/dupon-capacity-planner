"""
seed_config.py — Datos de configuración base (NO mock data).

Siembra SOLO lo que no viene de Odoo:
  - Compañías (con odoo_company_id real)
  - Configuración de silos (con odoo_location_id real)
  - Líneas de producción (capacidad teórica kg/h)
  - Tabla CON: consumos de referencia (Excel CON, kg/día por máquina)
  - Formatos por línea (Excel capacidades)
  - Usuarios de acceso

Lo que viene de Odoo (productos, workcenters, stock.quant, POs)
se importa mediante el sync engine (ODOO_MODE=real).

Uso:
  cd /ruta/al/proyecto
  .venv/bin/python3 seed_config.py

Idempotente: limpia solo tablas de configuración, preserva usuarios
y datos Odoo ya sincronizados.
"""
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_DB_PATH = os.path.join(_PROJECT_ROOT, "backend", "dev.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")
os.environ.setdefault("JWT_SECRET", "secreto_dev_32chars_minimo_ok_ok")
os.environ.setdefault("ODOO_MODE", "real")
os.environ.setdefault("APP_ENV", "development")

sys.path.insert(0, os.path.join(_PROJECT_ROOT, "backend"))

from sqlalchemy import text  # noqa: E402
from app.core.database import _IS_SQLITE, _sqlite_init, SessionLocal  # noqa: E402
from app.models.planner import (  # noqa: E402
    Company, SiloConfig, LineCapacity, RefConsumptionRate, LineFormat,
)

if _IS_SQLITE:
    _sqlite_init()

db = SessionLocal()

# ── Limpiar solo tablas de configuración ─────────────────────────────────────
# NO tocamos: users, stock_quants, purchase_orders, products, workcenters,
#             mrp_*, delivery_suggestions (los gestiona Odoo sync)
CONFIG_TABLES = [
    "line_formats",
    "ref_consumption_rates",
    "line_capacities",
    "silo_configs",
    "correction_factors",
    "delivery_suggestions",
]
for tbl in CONFIG_TABLES:
    try:
        db.execute(text(f"DELETE FROM {tbl}"))
    except Exception:
        pass
db.commit()
print("🗑️  Tablas de config limpiadas (stock/POs Odoo preservados)")

# ── Compañías ─────────────────────────────────────────────────────────────────
# odoo_company_id=1 → Dupon Biscuits Ibérica, S.A. (confirmado staging3)
companies = [
    Company(id=1, name="Dupon Biscuits Ibérica, S.A.", odoo_company_id=1, short_code="IBE"),
    Company(id=2, name="Dupon Deutschland GmbH",       odoo_company_id=8, short_code="GUD"),
    Company(id=3, name="Biscuits Dupon France",        odoo_company_id=3, short_code="FRA"),
    Company(id=4, name="Biscotti Dupon Italia",        odoo_company_id=4, short_code="ITA"),
    Company(id=5, name="Biscuits Dupon Belgium",       odoo_company_id=5, short_code="BEL"),
]
for c in companies:
    existing = db.query(Company).filter(Company.id == c.id).first()
    if existing:
        existing.name           = c.name
        existing.odoo_company_id = c.odoo_company_id
        existing.short_code     = c.short_code
    else:
        db.add(c)
db.commit()
print(f"✅ Compañías: {len(companies)}")

# ── Silos Ibérica — odoo_location_id confirmados en staging3 ─────────────────
# product_id Odoo: Harina=49486, Azúcar=49488, Aceite=49492
# location_id Odoo: Silo1=79, Silo2=80, Silo3=81, Azúcar=82, Aceite=83
silos = [
    SiloConfig(silo_code="S-H1", name="Silo Harina 1",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=79, odoo_product_id=49486),
    SiloConfig(silo_code="S-H2", name="Silo Harina 2",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=80, odoo_product_id=49486),
    SiloConfig(silo_code="S-H3", name="Silo Harina 3",
               material_type="harina", capacity_kg=25000, safety_stock_kg=2000,
               company_id=1, odoo_location_id=81, odoo_product_id=49486),
    SiloConfig(silo_code="S-AZ", name="Silo Azúcar",
               material_type="azucar", capacity_kg=30000, safety_stock_kg=2500,
               company_id=1, odoo_location_id=82, odoo_product_id=49488),
    SiloConfig(silo_code="S-AC", name="Silo Aceite Coco",
               material_type="aceite", capacity_kg=20000, safety_stock_kg=1500,
               company_id=1, odoo_location_id=83, odoo_product_id=49492),
]
db.add_all(silos)
db.commit()
print(f"✅ Silos IBE: {len(silos)}")

# ── Líneas de producción Ibérica (capacidad teórica kg/h) ────────────────────
line_data = [
    ("L01", 450), ("L02", 450), ("L03", 380),
    ("L04", 380), ("L05", 320), ("L06", 320),
    ("L07", 280), ("L08", 280), ("L09", 250),
    ("L10", 250),
]
lines = [LineCapacity(line_code=code, capacity_kg_h=kg_h, company_id=1)
         for code, kg_h in line_data]
db.add_all(lines)
db.commit()
print(f"✅ Líneas: {len(lines)}")

# ── Tabla CON — consumos de referencia (kg/día por 1 máquina, 24h) ────────────
# Fuente: hoja CON del Excel Apro-PM 2026.ods (Ibérica, company_id=1)
# Extracción: extract_con.py — 3 turnos × 8h por valor de turno = 24h
CON_DATA = [
    # ── STD_R_110 (Rotativa estándar 110mm) ──────────────────────────────────
    ("STD_R_110",    "harina",      1341),
    ("STD_R_110",    "azucar",       615),
    ("STD_R_110",    "aceite",        66),
    ("STD_R_110",    "lecitina",      30),
    ("STD_R_110",    "sal",           12),
    ("STD_R_110",    "carbonat",       0),
    ("STD_R_110",    "caramelina",     0),
    ("STD_R_110",    "maltitol",       0),
    ("STD_R_110",    "cacao",          0),
    ("STD_R_110",    "colorante",      0),
    ("STD_R_110",    "oli_bany",       0),
    # ── STD_R_SS (Rotativa sin azúcar) ───────────────────────────────────────
    ("STD_R_SS",     "harina",      1401),
    ("STD_R_SS",     "azucar",         0),
    ("STD_R_SS",     "aceite",        75),
    ("STD_R_SS",     "lecitina",      33),
    ("STD_R_SS",     "sal",           12),
    ("STD_R_SS",     "carbonat",       0),
    ("STD_R_SS",     "caramelina",     0),
    ("STD_R_SS",     "maltitol",     900),
    ("STD_R_SS",     "cacao",          0),
    ("STD_R_SS",     "colorante",      0),
    ("STD_R_SS",     "oli_bany",       0),
    # ── HAAS_110 (Horno wafer HAAS 110mm) ────────────────────────────────────
    ("HAAS_110",     "harina",     10503),
    ("HAAS_110",     "azucar",      4761),
    ("HAAS_110",     "aceite",       555),
    ("HAAS_110",     "lecitina",     237),
    ("HAAS_110",     "sal",           90),
    ("HAAS_110",     "carbonat",      36),
    ("HAAS_110",     "caramelina",    36),
    ("HAAS_110",     "maltitol",       0),
    ("HAAS_110",     "cacao",          0),
    ("HAAS_110",     "colorante",      0),
    ("HAAS_110",     "oli_bany",       0),
    # ── HAAS_98 (Horno wafer HAAS 98mm) ──────────────────────────────────────
    ("HAAS_98",      "harina",      9315),
    ("HAAS_98",      "azucar",      4224),
    ("HAAS_98",      "aceite",       492),
    ("HAAS_98",      "lecitina",     210),
    ("HAAS_98",      "sal",           78),
    ("HAAS_98",      "carbonat",      33),
    ("HAAS_98",      "caramelina",    30),
    ("HAAS_98",      "maltitol",       0),
    ("HAAS_98",      "cacao",          0),
    ("HAAS_98",      "colorante",      0),
    ("HAAS_98",      "oli_bany",       0),
    # ── HAAS_98_OREO (Mini 82 Oreo — HAAS 98 con cacao) ──────────────────────
    ("HAAS_98_OREO", "harina",       807),
    ("HAAS_98_OREO", "azucar",       405),
    ("HAAS_98_OREO", "aceite",        51),
    ("HAAS_98_OREO", "lecitina",      21),
    ("HAAS_98_OREO", "sal",            9),
    ("HAAS_98_OREO", "carbonat",       0),
    ("HAAS_98_OREO", "caramelina",     0),
    ("HAAS_98_OREO", "maltitol",       0),
    ("HAAS_98_OREO", "cacao",         96),
    ("HAAS_98_OREO", "colorante",     12),
    ("HAAS_98_OREO", "oli_bany",       0),
    # ── HAAS_110_OREO (HAAS 110 + variante oreo) ─────────────────────────────
    ("HAAS_110_OREO","harina",     10503),
    ("HAAS_110_OREO","azucar",      4761),
    ("HAAS_110_OREO","aceite",       555),
    ("HAAS_110_OREO","lecitina",     237),
    ("HAAS_110_OREO","sal",           90),
    ("HAAS_110_OREO","carbonat",      36),
    ("HAAS_110_OREO","caramelina",    36),
    ("HAAS_110_OREO","maltitol",       0),
    ("HAAS_110_OREO","cacao",         96),
    ("HAAS_110_OREO","colorante",      0),
    ("HAAS_110_OREO","oli_bany",       0),
    # ── MINI_75_SS (Mini 75mm sin azúcar) ────────────────────────────────────
    ("MINI_75_SS",   "harina",       723),
    ("MINI_75_SS",   "azucar",         0),
    ("MINI_75_SS",   "aceite",        39),
    ("MINI_75_SS",   "lecitina",      18),
    ("MINI_75_SS",   "sal",            6),
    ("MINI_75_SS",   "carbonat",       0),
    ("MINI_75_SS",   "caramelina",     0),
    ("MINI_75_SS",   "maltitol",     441),
    ("MINI_75_SS",   "cacao",          0),
    ("MINI_75_SS",   "colorante",      0),
    ("MINI_75_SS",   "oli_bany",       0),
    # ── MINI_75_OLI (Mini 75mm con aceite de baño) ───────────────────────────
    ("MINI_75_OLI",  "harina",       672),
    ("MINI_75_OLI",  "azucar",       309),
    ("MINI_75_OLI",  "aceite",       114),
    ("MINI_75_OLI",  "lecitina",      15),
    ("MINI_75_OLI",  "sal",            6),
    ("MINI_75_OLI",  "carbonat",       0),
    ("MINI_75_OLI",  "caramelina",     0),
    ("MINI_75_OLI",  "maltitol",       0),
    ("MINI_75_OLI",  "cacao",          0),
    ("MINI_75_OLI",  "colorante",      0),
    ("MINI_75_OLI",  "oli_bany",     495),
    # ── MINI_90_SS (Mini 90mm sin azúcar) ────────────────────────────────────
    ("MINI_90_SS",   "harina",      1131),
    ("MINI_90_SS",   "azucar",         0),
    ("MINI_90_SS",   "aceite",        60),
    ("MINI_90_SS",   "lecitina",      27),
    ("MINI_90_SS",   "sal",            9),
    ("MINI_90_SS",   "carbonat",       0),
    ("MINI_90_SS",   "caramelina",     0),
    ("MINI_90_SS",   "maltitol",     900),
    ("MINI_90_SS",   "cacao",          0),
    ("MINI_90_SS",   "colorante",      0),
    ("MINI_90_SS",   "oli_bany",       0),
    # ── MINI_90 (Mini 90mm estándar) ─────────────────────────────────────────
    ("MINI_90",      "harina",      1050),
    ("MINI_90",      "azucar",       483),
    ("MINI_90",      "aceite",        51),
    ("MINI_90",      "lecitina",      21),
    ("MINI_90",      "sal",            9),
    ("MINI_90",      "carbonat",       0),
    ("MINI_90",      "caramelina",     0),
    ("MINI_90",      "maltitol",       0),
    ("MINI_90",      "cacao",          0),
    ("MINI_90",      "colorante",      0),
    ("MINI_90",      "oli_bany",       0),
    # ── IMPERIAL (Cono imperial) ──────────────────────────────────────────────
    ("IMPERIAL",     "harina",      1419),
    ("IMPERIAL",     "azucar",       654),
    ("IMPERIAL",     "aceite",        72),
    ("IMPERIAL",     "lecitina",      30),
    ("IMPERIAL",     "sal",           12),
    ("IMPERIAL",     "carbonat",       0),
    ("IMPERIAL",     "caramelina",     0),
    ("IMPERIAL",     "maltitol",       0),
    ("IMPERIAL",     "cacao",          0),
    ("IMPERIAL",     "colorante",      0),
    ("IMPERIAL",     "oli_bany",       0),
    # ── SPECIAL (Barquillo cilíndrico estándar) ───────────────────────────────
    ("SPECIAL",      "harina",      1341),
    ("SPECIAL",      "azucar",       615),
    ("SPECIAL",      "aceite",        66),
    ("SPECIAL",      "lecitina",      30),
    ("SPECIAL",      "sal",           12),
    ("SPECIAL",      "carbonat",       0),
    ("SPECIAL",      "caramelina",     0),
    ("SPECIAL",      "maltitol",       0),
    ("SPECIAL",      "cacao",          0),
    ("SPECIAL",      "colorante",      0),
    ("SPECIAL",      "oli_bany",       0),
    # ── SPECIAL_SS (Barquillo cilíndrico sin azúcar) ──────────────────────────
    ("SPECIAL_SS",   "harina",      1341),
    ("SPECIAL_SS",   "azucar",         0),
    ("SPECIAL_SS",   "aceite",        66),
    ("SPECIAL_SS",   "lecitina",      30),
    ("SPECIAL_SS",   "sal",           12),
    ("SPECIAL_SS",   "carbonat",       0),
    ("SPECIAL_SS",   "caramelina",     0),
    ("SPECIAL_SS",   "maltitol",     900),
    ("SPECIAL_SS",   "cacao",          0),
    ("SPECIAL_SS",   "colorante",      0),
    ("SPECIAL_SS",   "oli_bany",       0),
]
con_records = [
    RefConsumptionRate(format_code=fc, material_type=mt, kg_per_day=kg, company_id=1)
    for fc, mt, kg in CON_DATA
]
db.add_all(con_records)
db.commit()
print(f"✅ CON rates: {len(con_records)}")

# ── Formatos por línea ────────────────────────────────────────────────────────
LINE_FORMAT_DATA = [
    # (line_code, format_code, machines)
    # ── Rotativas: L01, L02, L06 — múltiples cabezales posibles (hasta 9) ────
    ("L01", "STD_R_110",    2),
    ("L01", "STD_R_SS",     2),
    ("L02", "STD_R_110",    2),
    ("L02", "STD_R_SS",     2),
    ("L06", "STD_R_110",    3),
    ("L06", "STD_R_SS",     3),
    # ── Hornos lineales: siempre 1 máquina ───────────────────────────────────
    ("L03", "HAAS_110",     1),
    ("L03", "HAAS_98",      1),
    ("L03", "HAAS_98_OREO", 1),
    ("L04", "HAAS_110",     1),
    ("L04", "HAAS_98",      1),
    ("L04", "HAAS_110_OREO",1),
    ("L05", "MINI_75_SS",   1),
    ("L05", "MINI_75_OLI",  1),
    ("L07", "MINI_90",      1),
    ("L07", "MINI_90_SS",   1),
    ("L08", "IMPERIAL",     1),
    ("L09", "SPECIAL",      1),
    ("L09", "SPECIAL_SS",   1),
    ("L10", "SPECIAL",      1),
]
lf_records = [
    LineFormat(line_code=lc, format_code=fc, machines=m, company_id=1)
    for lc, fc, m in LINE_FORMAT_DATA
]
db.add_all(lf_records)
db.commit()
print(f"✅ Line formats: {len(lf_records)}")

db.close()
print()
print("🚀 Config seed completo. Ahora ejecuta el backend con ODOO_MODE=real")
print("   para importar productos, stock y POs desde Odoo staging3.")
