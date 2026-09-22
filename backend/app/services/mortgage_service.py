from app.db import connect
from app.repositories import loans, runs, settings
from app.services import assembly, snapshot

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, run_id): return runs.get(self._c, run_id)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12):
        # 组装：校验输入并调用摊还引擎得到全表
        full = assembly.assemble_schedule(principal, annual_rate, months)
        # 快照：裁剪与 JSON 序列化，persist 为假则不写入
        return snapshot.take_snapshot(
            self._c, full,
            {"principal": principal, "annual_rate": annual_rate, "months": months},
            loan_id, persist, preview_rows,
        )
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
