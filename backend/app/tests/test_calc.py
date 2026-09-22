import pytest
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.services import assembly, snapshot
from app.services.mortgage_service import MortgageService

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_assemble_returns_full_table():
    full = assembly.assemble_schedule(1_000_000, 3.5, 360)
    assert len(full["rows"]) == 360
    assert full["rows"][-1]["period"] == 360
    assert full["monthly_payment"] == 4490.45
    assert full["rows"][0]["interest"] == 2916.67

def test_assemble_rejects_bad_input():
    with pytest.raises(ValueError):
        assembly.assemble_schedule(0, 3.5, 360)
    with pytest.raises(ValueError):
        assembly.assemble_schedule(1000, -1, 360)
    with pytest.raises(ValueError):
        assembly.assemble_schedule(1000, 3.5, 0)

def test_snapshot_persisted_can_be_fetched_by_id():
    with MortgageService() as s:
        out = s.schedule(120000, 0, 12, None, True, preview_rows=6)
        assert out["run_id"] is not None
        assert out["monthly_payment"] == 10000.0
        assert len(out["preview"]) == 6
        assert out["row_count"] == 12
        fetched = s.run(out["run_id"])
    assert fetched is not None
    assert fetched["result"]["monthly_payment"] == 10000.0
    assert len(fetched["result"]["preview"]) == 6

def test_persist_false_does_not_write_snapshot():
    conn = connect()
    try:
        before = conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False)
        assert out["run_id"] is None
        assert len(out["preview"]) == 12
    conn = connect()
    try:
        after = conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()
    assert after == before

def test_snapshot_take_persist_false_skips_insert():
    full = assembly.assemble_schedule(120000, 0, 12)
    conn = connect()
    try:
        out = snapshot.take_snapshot(conn, full, {"principal": 120000, "annual_rate": 0, "months": 12}, None, False, 3)
    finally:
        conn.close()
    assert out["run_id"] is None
    assert len(out["preview"]) == 3
