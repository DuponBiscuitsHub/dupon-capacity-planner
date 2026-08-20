"""
tests/test_correction_engine.py — Tests del motor de auto-calibración.

Testea las funciones clave: get_active_factor (lookups + fallback),
_calculate_factor (sanity clamp, edge cases).
"""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.correction_engine import (
    _FACTOR_MAX,
    _FACTOR_MIN,
    _calculate_factor,
    get_active_factor,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _fake_silo(
    silo_code="S-H1",
    material_type="harina",
    odoo_product_id=49486,
    odoo_location_id=79,
):
    silo = MagicMock()
    silo.silo_code = silo_code
    silo.material_type = material_type
    silo.odoo_product_id = odoo_product_id
    silo.odoo_location_id = odoo_location_id
    return silo


def _fake_factor_row(
    factor=1.0,
    stock_actual_kg=20000,
    consumption_theoretical_kg=1500,
):
    row = MagicMock()
    row.factor = factor
    row.stock_actual_kg = stock_actual_kg
    row.consumption_theoretical_kg = consumption_theoretical_kg
    return row


# ── _calculate_factor ────────────────────────────────────────────────────

class TestCalculateFactor:
    def test_unmapped_silo_returns_none(self):
        """Silo sin odoo_product_id o location_id → None."""
        db = MagicMock()
        silo = _fake_silo(odoo_product_id=None, odoo_location_id=None)
        result = _calculate_factor(db, silo, date(2026, 8, 1), 1)
        assert result is None

    def test_no_stock_quant_returns_none(self):
        """Sin stock.quant en Odoo para el silo → None."""
        db = MagicMock()
        silo = _fake_silo()
        # _get_odoo_stock returns None when no quant found
        db.query.return_value.filter.return_value.first.return_value = None
        result = _calculate_factor(db, silo, date(2026, 8, 1), 1)
        assert result is None

    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_no_previous_factor_returns_baseline(self, mock_stock, mock_factor_row):
        """Sin factor del día anterior → baseline factor=1.0."""
        db = MagicMock()
        mock_stock.return_value = 18000.0
        mock_factor_row.return_value = None

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        assert result is not None
        assert result["factor"] == 1.0
        assert result["source"] == "auto"

    @patch("app.services.correction_engine._get_day_entries")
    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_normal_factor_calculation(self, mock_stock, mock_factor_row, mock_entries):
        """Factor normal: consumo_real/consumo_teórico."""
        db = MagicMock()
        mock_stock.return_value = 17000.0  # stock actual
        mock_factor_row.return_value = _fake_factor_row(
            stock_actual_kg=20000, consumption_theoretical_kg=1500,
        )
        mock_entries.return_value = 0.0  # sin entradas

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        # consumo_real = 20000 + 0 - 17000 = 3000
        # factor = 3000 / 1500 = 2.0 → exactamente en el límite → OK
        assert result["factor"] == 2.0

    @patch("app.services.correction_engine._get_day_entries")
    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_factor_clamped_above_max(self, mock_stock, mock_factor_row, mock_entries):
        """Factor > 2.0 se resetea a 1.0 por sanity."""
        db = MagicMock()
        mock_stock.return_value = 10000.0
        mock_factor_row.return_value = _fake_factor_row(
            stock_actual_kg=20000, consumption_theoretical_kg=1000,
        )
        mock_entries.return_value = 0.0

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        # consumo_real = 20000 + 0 - 10000 = 10000
        # factor = 10000 / 1000 = 10.0 → fuera de rango → clamp a 1.0
        assert result["factor"] == 1.0

    @patch("app.services.correction_engine._get_day_entries")
    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_factor_clamped_below_min(self, mock_stock, mock_factor_row, mock_entries):
        """Factor < 0.5 se resetea a 1.0 por sanity."""
        db = MagicMock()
        mock_stock.return_value = 19800.0
        mock_factor_row.return_value = _fake_factor_row(
            stock_actual_kg=20000, consumption_theoretical_kg=1000,
        )
        mock_entries.return_value = 0.0

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        # consumo_real = 20000 + 0 - 19800 = 200
        # factor = 200 / 1000 = 0.2 → fuera de rango → clamp a 1.0
        assert result["factor"] == 1.0

    @patch("app.services.correction_engine._get_day_entries")
    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_zero_theoretical_uses_one(self, mock_stock, mock_factor_row, mock_entries):
        """Si consumo teórico = 0, factor = 1.0."""
        db = MagicMock()
        mock_stock.return_value = 20000.0
        mock_factor_row.return_value = _fake_factor_row(
            stock_actual_kg=20000, consumption_theoretical_kg=0,
        )
        mock_entries.return_value = 0.0

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        assert result["factor"] == 1.0

    @patch("app.services.correction_engine._get_day_entries")
    @patch("app.services.correction_engine._get_factor_row")
    @patch("app.services.correction_engine._get_odoo_stock")
    def test_entries_increase_expected_stock(self, mock_stock, mock_factor_row, mock_entries):
        """Las entradas del día se suman al stock esperado."""
        db = MagicMock()
        mock_stock.return_value = 30000.0
        mock_factor_row.return_value = _fake_factor_row(
            stock_actual_kg=20000, consumption_theoretical_kg=1000,
        )
        mock_entries.return_value = 25000.0  # cisterna de harina

        result = _calculate_factor(db, _fake_silo(), date(2026, 8, 1), 1)
        # consumo_real = 20000 + 25000 - 30000 = 15000
        # factor = 15000 / 1000 = 15.0 → fuera de rango → 1.0
        assert result["factor"] == 1.0


# ── get_active_factor ──────────────────────────────────────────────────────

class TestGetActiveFactor:
    @patch("app.services.correction_engine._get_factor_row")
    def test_today_factor_takes_priority(self, mock_row):
        """Si hay factor de hoy, se usa directamente."""
        db = MagicMock()
        mock_row.return_value = _fake_factor_row(factor=1.15)

        result = get_active_factor(db, "harina", 1)
        assert result == 1.15

    @patch("app.services.correction_engine._get_factor_row")
    def test_no_today_uses_average(self, mock_row):
        """Sin factor de hoy, usa media de los últimos días."""
        db = MagicMock()
        mock_row.return_value = None  # sin factor de hoy

        # Simular query de histórico
        r1, r2, r3 = MagicMock(), MagicMock(), MagicMock()
        r1.factor = 1.10
        r2.factor = 1.20
        r3.factor = 1.30
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [r1, r2, r3]

        result = get_active_factor(db, "harina", 1)
        expected = round((1.10 + 1.20 + 1.30) / 3, 4)
        assert result == expected

    @patch("app.services.correction_engine._get_factor_row")
    def test_no_history_returns_one(self, mock_row):
        """Sin factor de hoy ni histórico → 1.0 (sin corrección)."""
        db = MagicMock()
        mock_row.return_value = None
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = get_active_factor(db, "harina", 1)
        assert result == 1.0
