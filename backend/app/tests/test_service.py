import json
import pytest
from app import db, seed
from app.services.mortgage_service import MortgageService
from app.services.schedule_pipeline import assemble_schedule, snapshot_schedule

@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    with MortgageService() as s:
        yield s

def test_assemble_returns_full_table():
    full = assemble_schedule(1_000_000, 3.5, 360)
    assert len(full["rows"]) == 360
    assert full["monthly_payment"] == 4490.45
    assert full["rows"][0]["interest"] == 2916.67

def test_assemble_zero_rate_lock():
    assert assemble_schedule(120000, 0, 12)["monthly_payment"] == 10000.0

def test_assemble_validation():
    with pytest.raises(ValueError):
        assemble_schedule(0, 3.5, 360)
    with pytest.raises(ValueError):
        assemble_schedule(100000, -1, 360)
    with pytest.raises(ValueError):
        assemble_schedule(100000, 3.5, 0)

def test_snapshot_trims_and_serializes():
    snap = snapshot_schedule(assemble_schedule(1_000_000, 3.5, 360), preview_rows=12)
    assert snap.result["row_count"] == 360
    assert len(snap.result["preview"]) == 12
    assert json.loads(snap.result_json) == snap.result

def test_snapshot_write_then_fetch_by_id(svc):
    res = svc.schedule(1_000_000, 3.5, 360, None, True, preview_rows=12)
    assert res["run_id"] is not None
    result = json.loads(svc.run(res["run_id"])["result_json"])
    assert result["monthly_payment"] == 4490.45
    assert len(result["preview"]) == 12

def test_no_persist_skips_snapshot_write(svc):
    before = len(svc.history(1000))
    res = svc.schedule(1_000_000, 3.5, 360, None, False)
    assert res["run_id"] is None
    assert res["monthly_payment"] == 4490.45
    assert len(svc.history(1000)) == before
