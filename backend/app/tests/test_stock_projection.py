"""
tests/test_stock_projection.py — Tests de la simulación de stock forward.

_simulate es una función pura: no toca BD.
"""
from datetime import date

from app.services.stock_projection import _simulate


class TestSimulate:
    START = date(2026, 8, 1)

    def test_zero_consumption_stock_stays(self):
        """Sin consumo, el stock no baja."""
        points = _simulate(
            stock_kg=10000, consumption_kg_day=0,
            po_events=[], capacity_kg=25000,
            start=self.START, days=3,
        )
        assert len(points) == 4  # día 0 + 3 días
        assert all(p["stock_kg"] == 10000 for p in points)

    def test_consumption_reduces_stock(self):
        """El consumo diario reduce el stock linealmente."""
        points = _simulate(
            stock_kg=10000, consumption_kg_day=2000,
            po_events=[], capacity_kg=25000,
            start=self.START, days=3,
        )
        assert points[0]["stock_kg"] == 10000      # día 0
        assert points[1]["stock_kg"] == 8000        # día 1
        assert points[2]["stock_kg"] == 6000        # día 2
        assert points[3]["stock_kg"] == 4000        # día 3

    def test_stock_floors_at_zero(self):
        """El stock nunca baja de 0."""
        points = _simulate(
            stock_kg=1000, consumption_kg_day=2000,
            po_events=[], capacity_kg=25000,
            start=self.START, days=3,
        )
        assert points[0]["stock_kg"] == 1000
        assert points[1]["stock_kg"] == 0           # floor: 1000 - 2000 = -1000 → 0
        assert points[2]["stock_kg"] == 0           # sigue en 0
        assert points[3]["stock_kg"] == 0

    def test_po_adds_stock(self):
        """Una PO planificada suma stock en la fecha correcta."""
        points = _simulate(
            stock_kg=5000, consumption_kg_day=1000,
            po_events=[{"date": "2026-08-04", "qty_kg": 20000, "po_name": "PO001"}],
            capacity_kg=25000,
            start=self.START, days=3,
        )
        assert points[0]["stock_kg"] == 5000        # día 0 (08-01)
        assert points[1]["stock_kg"] == 4000        # día 1 (08-02): -1000
        assert points[2]["stock_kg"] == 3000        # día 2 (08-03): -1000
        # día 3 (08-04): -1000 + 20000 = 22000
        assert points[3]["stock_kg"] == 22000

    def test_po_capped_at_capacity(self):
        """El stock no supera la capacidad del silo tras una PO grande."""
        points = _simulate(
            stock_kg=20000, consumption_kg_day=0,
            po_events=[{"date": "2026-08-02", "qty_kg": 10000, "po_name": "PO001"}],
            capacity_kg=25000,
            start=self.START, days=2,
        )
        # día 1 (2026-08-02): 20000 + 10000 = 30000 → cap → 25000
        assert points[1]["stock_kg"] == 25000

    def test_multiple_pos_same_day(self):
        """Múltiples POs en el mismo día se suman."""
        points = _simulate(
            stock_kg=5000, consumption_kg_day=0,
            po_events=[
                {"date": "2026-08-02", "qty_kg": 3000, "po_name": "PO001"},
                {"date": "2026-08-02", "qty_kg": 2000, "po_name": "PO002"},
            ],
            capacity_kg=25000,
            start=self.START, days=1,
        )
        # día 1: 5000 + 3000 + 2000 = 10000
        assert points[1]["stock_kg"] == 10000

    def test_first_point_is_current_stock(self):
        """El primer punto siempre refleja el stock actual sin consumo."""
        points = _simulate(
            stock_kg=15000, consumption_kg_day=5000,
            po_events=[], capacity_kg=25000,
            start=self.START, days=1,
        )
        assert points[0]["stock_kg"] == 15000  # sin consumo en día 0
        assert points[1]["stock_kg"] == 10000  # consumo en día 1

    def test_dates_are_correct(self):
        """Los puntos tienen las fechas correctas."""
        points = _simulate(
            stock_kg=10000, consumption_kg_day=0,
            po_events=[], capacity_kg=25000,
            start=date(2026, 8, 15), days=3,
        )
        assert points[0]["date"] == "2026-08-15"
        assert points[1]["date"] == "2026-08-16"
        assert points[2]["date"] == "2026-08-17"
        assert points[3]["date"] == "2026-08-18"

    def test_stock_zero_then_po_arrives(self):
        """Edge case: stock llega a 0, luego una PO lo recupera."""
        points = _simulate(
            stock_kg=1000, consumption_kg_day=2000,
            po_events=[{"date": "2026-08-04", "qty_kg": 10000, "po_name": "PO001"}],
            capacity_kg=25000,
            start=self.START, days=3,
        )
        assert points[0]["stock_kg"] == 1000        # día 0 (08-01)
        assert points[1]["stock_kg"] == 0           # día 1 (08-02): floor
        assert points[2]["stock_kg"] == 0           # día 2 (08-03): sigue en 0
        # día 3 (08-04): 0 - 2000 + 10000 = 8000
        assert points[3]["stock_kg"] == 8000
