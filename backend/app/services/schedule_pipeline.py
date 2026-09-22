import json
from dataclasses import dataclass
from app.engines.amortization import equal_payment_schedule

SUMMARY_KEYS = ("monthly_payment", "total_interest", "total_payment")

@dataclass
class ScheduleSnapshot:
    result: dict       # 裁剪后的摘要 + 预览
    result_json: str   # 序列化后的快照，供写入 calc_runs

def assemble_schedule(principal: float, annual_rate: float, months: int) -> dict:
    """组装步骤：校验输入并调用摊还引擎，返回含全表的结果。"""
    if principal <= 0:
        raise ValueError("principal")
    if annual_rate < 0:
        raise ValueError("annual_rate")
    if months <= 0:
        raise ValueError("months")
    return equal_payment_schedule(principal, annual_rate, months)

def snapshot_schedule(full: dict, preview_rows: int = 12) -> ScheduleSnapshot:
    """快照步骤：把全表裁剪成摘要+预览，并序列化为写入 calc_runs 的 JSON。"""
    out = {k: full[k] for k in SUMMARY_KEYS}
    out["preview"] = full["rows"][:preview_rows]
    out["row_count"] = len(full["rows"])
    return ScheduleSnapshot(out, json.dumps(out, ensure_ascii=False))
