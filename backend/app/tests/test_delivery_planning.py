"""
tests/test_delivery_planning.py — Tests de la lógica de semáforo y editabilidad.

_compute_timing_color y _compute_editability son funciones puras con inputs
simples, lo que permite testearlas sin DB.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.services.delivery_planning import (
    _compute_editability,
    _compute_timing_color,
)


# ── _compute_timing_color ────────────────────────────────────────────────────

class TestComputeTimingColor:
    def _make_po(self, date_planned: datetime | None) -> MagicMock:
        po = MagicMock()
        po.date_planned = date_planned
        return po

    def test_no_app_date_returns_green(self):
        """Sin fecha sugerida por la app → green por defecto."""
        po = self._make_po(datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc))
        assert _compute_timing_color(po, None) == "green"

    def test_no_po_date_returns_green(self):
        """PO sin date_planned → green por defecto."""
        po = self._make_po(None)
        app_date = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
        assert _compute_timing_color(po, app_date) == "green"

    def test_on_time_returns_green(self):
        """PO llega antes de la fecha sugerida + tolerancia → green."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po = self._make_po(app_date)  # exacto
        assert _compute_timing_color(po, app_date) == "green"

    def test_within_tolerance_returns_green(self):
        """PO llega dentro de las 24h de tolerancia → green."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po_date = app_date + timedelta(hours=23)  # 1h antes del límite
        po = self._make_po(po_date)
        assert _compute_timing_color(po, app_date) == "green"

    def test_exactly_at_tolerance_returns_green(self):
        """PO llega exactamente en el límite → green (<=)."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po_date = app_date + timedelta(hours=24)  # exacto en el límite
        po = self._make_po(po_date)
        assert _compute_timing_color(po, app_date) == "green"

    def test_late_returns_orange(self):
        """PO llega después de la tolerancia → orange."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po_date = app_date + timedelta(hours=25)  # 1h después del límite
        po = self._make_po(po_date)
        assert _compute_timing_color(po, app_date) == "orange"

    def test_very_late_returns_orange(self):
        """PO llega mucho después → sigue siendo orange (no red)."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po_date = app_date + timedelta(days=7)
        po = self._make_po(po_date)
        assert _compute_timing_color(po, app_date) == "orange"

    def test_early_returns_green(self):
        """PO llega antes de la fecha sugerida → green."""
        app_date = datetime(2026, 8, 10, 8, 0, tzinfo=timezone.utc)
        po_date = app_date - timedelta(days=3)
        po = self._make_po(po_date)
        assert _compute_timing_color(po, app_date) == "green"


# ── _compute_editability ────────────────────────────────────────────────────

class TestComputeEditability:
    def _make_po(self, state: str, vendor_confirmed: bool = False) -> MagicMock:
        po = MagicMock()
        po.state = state
        po.vendor_confirmed = vendor_confirmed
        return po

    def test_done_is_blocked(self):
        """PO en estado 'done' no se puede editar."""
        po = self._make_po("done")
        can_edit, warning = _compute_editability(po)
        assert can_edit is False
        assert warning == "poEditBlocked"

    def test_cancel_is_blocked(self):
        """PO en estado 'cancel' no se puede editar."""
        po = self._make_po("cancel")
        can_edit, warning = _compute_editability(po)
        assert can_edit is False
        assert warning == "poEditBlocked"

    def test_draft_is_editable_no_warning(self):
        """PO en draft sin confirmación de proveedor → editable sin warning."""
        po = self._make_po("draft")
        can_edit, warning = _compute_editability(po)
        assert can_edit is True
        assert warning is None

    def test_purchase_is_editable_no_warning(self):
        """PO en estado 'purchase' sin vendor_confirmed → editable sin warning."""
        po = self._make_po("purchase")
        can_edit, warning = _compute_editability(po)
        assert can_edit is True
        assert warning is None

    def test_vendor_confirmed_editable_with_warning(self):
        """PO con vendor_confirmed=True → editable pero con warning."""
        po = self._make_po("purchase", vendor_confirmed=True)
        can_edit, warning = _compute_editability(po)
        assert can_edit is True
        assert warning == "poEditWarningConfirmed"

    def test_draft_vendor_confirmed_still_has_warning(self):
        """Incluso en draft, si vendor_confirmed → warning."""
        po = self._make_po("draft", vendor_confirmed=True)
        can_edit, warning = _compute_editability(po)
        assert can_edit is True
        assert warning == "poEditWarningConfirmed"
