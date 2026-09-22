"""快照步骤：把全表裁剪成预览并 JSON 序列化后写入 calc_runs。"""
import json

from app.repositories import runs

KIND = "schedule"


def trim_schedule(full: dict, preview_rows: int = 12) -> dict:
    """从全表裁出持久化/响应所需的摘要与预览行。"""
    return {
        "monthly_payment": full["monthly_payment"],
        "total_interest": full["total_interest"],
        "total_payment": full["total_payment"],
        "preview": full["rows"][:preview_rows],
        "row_count": len(full["rows"]),
    }


def take_snapshot(conn, full: dict, inputs: dict, loan_id, persist: bool, preview_rows: int = 12) -> dict:
    """裁剪全表；persist 为真时序列化并写入快照，否则不触发任何写入。"""
    slim = trim_schedule(full, preview_rows)
    run_id = None
    if persist:
        run_id = runs.insert(
            conn,
            KIND,
            json.dumps(inputs, ensure_ascii=False),
            json.dumps(slim, ensure_ascii=False),
            loan_id,
        )
    return {"run_id": run_id, **slim}
