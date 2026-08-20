"""
tests/test_delivery_calculator.py — Tests del motor de cálculo de entregas.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.services.delivery_calculator import (
    _calculate_consumption_rate,
    _get_silo_stock,
    recalculate_deliveries,
)


class _FakeSilo:
    def __init__(self, silo_code, material_type, capacity_kg, safety_stock_kg,
                 odoo_location_id=None, odoo_product_id=None, company_id=1):
        self.silo_code = silo_code
        self.material_type = material_type
        self.capacity_kg = capacity_kg
        self.safety_stock_kg = safety_stock_kg
        self.odoo_location_id = odoo_location_id
        self.odoo_product_id = odoo_product_id
        self.company_id = company_id


def test_get_silo_stock_returns_none_without_location():
    """Si location_id o product_id son None, retorna None (TBD no resuelto)."""
    db = MagicMock()
    silo = _FakeSilo("S-H1", "harina", 25000, 2000)
    result = _get_silo_stock(db, silo)
    assert result is None


def test_get_silo_stock_returns_quantity():
    """Retorna la cantidad del quant si location e product están configurados."""
    db = MagicMock()
    silo = _FakeSilo("S-H1", "harina", 25000, 2000, odoo_location_id=10, odoo_product_id=5)
    mock_quant = MagicMock()
    mock_quant.quantity = 18000.0
    db.query.return_value.filter.return_value.first.return_value = mock_quant

    result = _get_silo_stock(db, silo)
    assert result == 18000.0


def test_get_silo_stock_returns_zero_when_no_quant():
    """Retorna 0.0 si no hay quant (ubicación vacía, no None)."""
    db = MagicMock()
    silo = _FakeSilo("S-H1", "harina", 25000, 2000, odoo_location_id=10, odoo_product_id=5)
    db.query.return_value.filter.return_value.first.return_value = None

    result = _get_silo_stock(db, silo)
    assert result == 0.0


def test_recalculate_no_silos_returns_empty():
    """Si no hay silos configurados, retorna lista vacía."""
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    result = recalculate_deliveries(db, company_id=1)
    assert result == []


def test_recalculate_skips_silos_without_location():
    """Silos sin location_id/product_id configurados se omiten."""
    db = MagicMock()
    silo_no_config = _FakeSilo("S-H1", "harina", 25000, 2000)  # sin location/product

    # Simular query de silos
    call_count = 0
    def side_effect(model):
        nonlocal call_count
        call_count += 1
        m = MagicMock()
        if call_count == 1:  # Primera query → silos
            m.filter.return_value.all.return_value = [silo_no_config]
        else:
            m.filter.return_value.all.return_value = []
        return m

    db.query.side_effect = side_effect
    result = recalculate_deliveries(db, company_id=1)
    assert result == []
