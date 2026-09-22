import json, sqlite3
from datetime import datetime, timezone

def insert(conn, kind, input_json, result_json, loan_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,loan_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, loan_id, input_json, result_json, now))
    conn.commit(); return int(cur.lastrowid)

def get(conn, run_id):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        return None
    item = dict(row)
    item["input"] = json.loads(item.pop("input_json"))
    item["result"] = json.loads(item.pop("result_json"))
    return item

def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
