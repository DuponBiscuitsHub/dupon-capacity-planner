"""
scripts/seed_dev_data.py — Seed de datos de desarrollo para SQLite.

Inserta los datos que en producción vienen de las migraciones Alembic:
  - Silos Ibérica (5)
  - Líneas L01-L10 (10)
  - Tabla CON: ref_consumption_rates (~170 filas)
  - Line_formats: mapping línea → formato (~20 filas)
  - Stock simulado para visualizar gauges

Uso:
  cd backend
  env -i DATABASE_URL="sqlite:///./dev.db" JWT_SECRET="..." ODOO_MODE=mock \
    ../.venv/bin/python3 scripts/seed_dev_data.py

Idempotente: verifica si los datos ya existen antes de insertar.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import _IS_SQLITE, _sqlite_init, SessionLocal
from datetime import datetime, timedelta, timezone

from app.models.planner import (
    SiloConfig, LineCapacity, RefConsumptionRate, LineFormat,
)
from app.models.odoo_replica import Product, StockQuant, PurchaseOrder


def seed_silos(db) -> int:
    if db.query(SiloConfig).count() > 0:
        return 0
    silos = [
        SiloConfig(silo_code="S-H1", name="Silo Harina 1", material_type="harina",
                   capacity_kg=25000, safety_stock_kg=2000, company_id=1,
                   odoo_location_id=79, odoo_product_id=49486),
        SiloConfig(silo_code="S-H2", name="Silo Harina 2", material_type="harina",
                   capacity_kg=25000, safety_stock_kg=2000, company_id=1,
                   odoo_location_id=80, odoo_product_id=49486),
        SiloConfig(silo_code="S-H3", name="Silo Harina 3", material_type="harina",
                   capacity_kg=25000, safety_stock_kg=2000, company_id=1,
                   odoo_location_id=81, odoo_product_id=49486),
        SiloConfig(silo_code="S-AZ", name="Silo Azúcar", material_type="azucar",
                   capacity_kg=30000, safety_stock_kg=2500, company_id=1,
                   odoo_location_id=82, odoo_product_id=49488),
        SiloConfig(silo_code="S-AC", name="Silo Aceite Coco", material_type="aceite",
                   capacity_kg=20000, safety_stock_kg=1500, company_id=1,
                   odoo_location_id=83, odoo_product_id=49492),
    ]
    db.add_all(silos)
    return len(silos)


def seed_lines(db) -> int:
    if db.query(LineCapacity).count() > 0:
        return 0
    lines = [
        LineCapacity(line_code=f"L{i:02d}", capacity_kg_h=0, company_id=1)
        for i in range(1, 11)
    ]
    db.add_all(lines)
    return len(lines)


def seed_consumption_rates(db) -> int:
    if db.query(RefConsumptionRate).count() > 0:
        return 0

    # Datos de la hoja CON del Apro-PM 2026.ods
    # Formato: (format_code, material_type, kg_per_day)
    _RATES = [
        # HARINA
        ("STD_R_110", "harina", 447), ("STD_R_SS", "harina", 467),
        ("HAAS_110", "harina", 3501), ("HAAS_98", "harina", 3105),
        ("MINI_75_SS", "harina", 241), ("MINI_75_OLI", "harina", 224),
        ("MINI_90_SS", "harina", 377), ("MINI_90", "harina", 350),
        ("IMPERIAL", "harina", 473), ("MINI_82", "harina", 303),
        ("MINI_82_OREO", "harina", 269), ("BONCOLAC", "harina", 447),
        ("HAAS_98_OREO", "harina", 3105), ("HAAS_110_OREO", "harina", 3501),
        # AZÚCAR
        ("STD_R_110", "azucar", 205), ("STD_R_SS", "azucar", 0),
        ("HAAS_110", "azucar", 1587), ("HAAS_98", "azucar", 1408),
        ("MINI_75_SS", "azucar", 0), ("MINI_75_OLI", "azucar", 103),
        ("MINI_90_SS", "azucar", 0), ("MINI_90", "azucar", 161),
        ("IMPERIAL", "azucar", 218), ("MINI_82", "azucar", 140),
        ("MINI_82_OREO", "azucar", 135), ("BONCOLAC", "azucar", 205),
        ("HAAS_98_OREO", "azucar", 1408), ("HAAS_110_OREO", "azucar", 1587),
        # ACEITE
        ("STD_R_110", "aceite", 22), ("STD_R_SS", "aceite", 25),
        ("HAAS_110", "aceite", 185), ("HAAS_98", "aceite", 164),
        ("MINI_75_SS", "aceite", 13), ("MINI_75_OLI", "aceite", 38),
        ("MINI_90_SS", "aceite", 20), ("MINI_90", "aceite", 17),
        ("IMPERIAL", "aceite", 24), ("MINI_82", "aceite", 15),
        ("MINI_82_OREO", "aceite", 17), ("BONCOLAC", "aceite", 22),
        ("HAAS_98_OREO", "aceite", 164), ("HAAS_110_OREO", "aceite", 185),
        # LECITINA
        ("STD_R_110", "lecitina", 10), ("STD_R_SS", "lecitina", 11),
        ("HAAS_110", "lecitina", 79), ("HAAS_98", "lecitina", 70),
        ("MINI_75_SS", "lecitina", 6), ("MINI_75_OLI", "lecitina", 5),
        ("MINI_90_SS", "lecitina", 9), ("MINI_90", "lecitina", 7),
        ("IMPERIAL", "lecitina", 10), ("MINI_82", "lecitina", 6),
        ("MINI_82_OREO", "lecitina", 7), ("BONCOLAC", "lecitina", 10),
        ("HAAS_98_OREO", "lecitina", 70), ("HAAS_110_OREO", "lecitina", 79),
        # SAL
        ("STD_R_110", "sal", 4), ("STD_R_SS", "sal", 4),
        ("HAAS_110", "sal", 30), ("HAAS_98", "sal", 26),
        ("MINI_75_SS", "sal", 2), ("MINI_75_OLI", "sal", 2),
        ("MINI_90_SS", "sal", 3), ("MINI_90", "sal", 3),
        ("IMPERIAL", "sal", 4), ("MINI_82", "sal", 3),
        ("MINI_82_OREO", "sal", 3), ("BONCOLAC", "sal", 4),
        ("HAAS_98_OREO", "sal", 26), ("HAAS_110_OREO", "sal", 30),
        # CARBONAT
        ("HAAS_110", "carbonat", 12), ("HAAS_98", "carbonat", 11),
        ("HAAS_98_OREO", "carbonat", 11), ("HAAS_110_OREO", "carbonat", 12),
        # CARAMELINA
        ("HAAS_110", "caramelina", 12), ("HAAS_98", "caramelina", 10),
        # MALTITOL (formatos sin azúcar)
        ("STD_R_SS", "maltitol", 300), ("MINI_75_SS", "maltitol", 147),
        ("MINI_90_SS", "maltitol", 300),
        # CACAO (oreo)
        ("MINI_82_OREO", "cacao", 32),
        ("HAAS_98_OREO", "cacao", 32), ("HAAS_110_OREO", "cacao", 32),
        # COLORANTE (oreo)
        ("MINI_82_OREO", "colorante", 4),
        ("HAAS_98_OREO", "colorante", 4), ("HAAS_110_OREO", "colorante", 4),
        # OLI BANY
        ("MINI_75_OLI", "oli_bany", 165),
    ]
    rates = [
        RefConsumptionRate(format_code=fc, material_type=mt, kg_per_day=kg, company_id=1)
        for fc, mt, kg in _RATES
    ]
    db.add_all(rates)
    return len(rates)


def seed_line_formats(db) -> int:
    if db.query(LineFormat).count() > 0:
        return 0

    _FORMATS = [
        # Rotativos (8 hornos cada línea)
        ("L01_L02", "STD_R_110", 8), ("L01_L02", "STD_R_SS", 8),
        ("L06", "STD_R_110", 8), ("L06", "STD_R_SS", 8),
        # Lineales HAAS
        ("L03", "HAAS_110", 1), ("L03", "HAAS_110_OREO", 1),
        ("L04", "HAAS_110", 1), ("L04", "HAAS_98", 1),
        ("L04", "HAAS_98_OREO", 1), ("L04", "HAAS_110_OREO", 1),
        ("L07", "HAAS_110", 1),
        ("L09", "HAAS_98", 1), ("L09", "HAAS_98_OREO", 1),
        ("L10", "HAAS_98", 1), ("L10", "HAAS_98_OREO", 1),
        # Lineales Mini
        ("L05", "MINI_75_SS", 1), ("L05", "MINI_75_OLI", 1),
        ("L05", "MINI_82", 1),
        ("L08", "MINI_82", 1), ("L08", "MINI_82_OREO", 1),
    ]
    formats = [
        LineFormat(line_code=lc, format_code=fc, machines=m, company_id=1)
        for lc, fc, m in _FORMATS
    ]
    db.add_all(formats)
    return len(formats)


def seed_products(db) -> int:
    """Inserta productos de primera materia (FK requerida por stock_quants)."""
    if db.query(Product).count() > 0:
        return 0
    products = [
        Product(odoo_id=49486, name="Harina de trigo", default_code="RM-HAR", company_id=1),
        Product(odoo_id=49488, name="Azúcar blanco", default_code="RM-AZU", company_id=1),
        Product(odoo_id=49492, name="Aceite de coco", default_code="RM-ACE", company_id=1),
    ]
    db.add_all(products)
    return len(products)


def seed_mock_stock(db) -> int:
    """Inserta stock simulado para que los gauges muestren datos."""
    if db.query(StockQuant).count() > 0:
        return 0

    # Stock variado para visualización
    _STOCK = [
        (79, 49486, 18500, 1),  # S-H1: 74%
        (80, 49486, 12000, 1),  # S-H2: 48%
        (81, 49486, 4200, 1),   # S-H3: 17% (critical)
        (82, 49488, 22000, 1),  # S-AZ: 73%
        (83, 49492, 6500, 1),   # S-AC: 33% (warning)
    ]
    quants = [
        StockQuant(
            odoo_id=1000 + i,
            product_id=pid,
            location_id=lid,
            quantity=qty,
            company_id=cid,
        )
        for i, (lid, pid, qty, cid) in enumerate(_STOCK)
    ]
    db.add_all(quants)
    return len(quants)


def seed_mock_purchase_orders(db) -> int:
    """Inserta POs simuladas para que el timeline de entregas muestre datos."""
    if db.query(PurchaseOrder).count() > 0:
        return 0

    now = datetime.now(timezone.utc)
    pos = [
        # Harina — entrega en 3 días, confirmada
        PurchaseOrder(
            odoo_id=5001, order_odoo_id=3001, name="PO-00201",
            partner_name="Harinera del Mediterráneo",
            vendor_confirmed=True,
            product_id=49486, quantity=25000,
            date_planned=now + timedelta(days=3),
            state="purchase", company_id=1,
        ),
        # Harina — entrega en 10 días, draft
        PurchaseOrder(
            odoo_id=5002, order_odoo_id=3002, name="PO-00202",
            partner_name="Harinera del Mediterráneo",
            vendor_confirmed=False,
            product_id=49486, quantity=25000,
            date_planned=now + timedelta(days=10),
            state="draft", company_id=1,
        ),
        # Azúcar — entrega en 5 días
        PurchaseOrder(
            odoo_id=5003, order_odoo_id=3003, name="PO-00203",
            partner_name="Azucarera Ebro",
            vendor_confirmed=True,
            product_id=49488, quantity=28000,
            date_planned=now + timedelta(days=5),
            state="purchase", company_id=1,
        ),
        # Aceite — entrega en 2 días (urgente)
        PurchaseOrder(
            odoo_id=5004, order_odoo_id=3004, name="PO-00204",
            partner_name="Aceites del Sur",
            vendor_confirmed=False,
            product_id=49492, quantity=18000,
            date_planned=now + timedelta(days=2),
            state="draft", company_id=1,
        ),
        # Aceite — entrega en 15 días
        PurchaseOrder(
            odoo_id=5005, order_odoo_id=3005, name="PO-00205",
            partner_name="Aceites del Sur",
            vendor_confirmed=True,
            product_id=49492, quantity=18000,
            date_planned=now + timedelta(days=15),
            state="purchase", company_id=1,
        ),
    ]
    db.add_all(pos)
    return len(pos)


def main():
    if _IS_SQLITE:
        _sqlite_init()

    db = SessionLocal()
    try:
        n_silos = seed_silos(db)
        n_lines = seed_lines(db)
        n_rates = seed_consumption_rates(db)
        n_formats = seed_line_formats(db)
        n_products = seed_products(db)
        n_stock = seed_mock_stock(db)
        n_pos = seed_mock_purchase_orders(db)
        db.commit()

        print(f"✅ Seed completado:")
        print(f"   Silos:       {n_silos} insertados")
        print(f"   Líneas:      {n_lines} insertadas")
        print(f"   Consumos:    {n_rates} insertados")
        print(f"   LineFormats: {n_formats} insertados")
        print(f"   Products:    {n_products} insertados")
        print(f"   Stock mock:  {n_stock} insertados")
        print(f"   POs mock:    {n_pos} insertados")
        totals = [n_silos, n_lines, n_rates, n_formats, n_products, n_stock, n_pos]
        if all(n == 0 for n in totals):
            print("   (todos los datos ya existían)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
