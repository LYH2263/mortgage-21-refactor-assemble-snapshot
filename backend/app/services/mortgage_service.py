from app.db import connect
from app.repositories import loans, runs, settings
from app.services.schedule_pipeline import assemble_schedule, snapshot_schedule

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, rid): return runs.get(self._c, rid)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12):
        full = assemble_schedule(principal, annual_rate, months)
        snap = snapshot_schedule(full, preview_rows)
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {"principal": principal, "annual_rate": annual_rate, "months": months}, snap.result_json, loan_id)
        return {"run_id": rid, **snap.result}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
