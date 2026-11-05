"""SQLite-backed storage for part requests and the decision history."""
import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.exceptions import NotFoundError
from app.schemas.request import PartRequestCreate, RequestStatus

_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_name TEXT NOT NULL,
    equipment TEXT NOT NULL DEFAULT '',
    part_description TEXT NOT NULL,
    part_number TEXT NOT NULL DEFAULT '',
    quantity INTEGER NOT NULL DEFAULT 1,
    priority TEXT NOT NULL DEFAULT 'normal',
    notes TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    source TEXT NOT NULL,
    summary TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class WorkshopService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._lock = threading.Lock()
        # One shared connection guarded by a lock (works for in-memory DBs in tests too).
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    # ---------- requests ----------
    def create_request(self, data: PartRequestCreate) -> dict[str, Any]:
        now = _now()
        with self._lock:
            cur = self._conn.execute(
                """INSERT INTO requests (requester_name, equipment, part_description, part_number,
                   quantity, priority, notes, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (data.requester_name, data.equipment, data.part_description, data.part_number,
                 data.quantity, data.priority.value, data.notes, now, now),
            )
            self._conn.commit()
            request_id = cur.lastrowid
        self.add_decision(request_id, "created", "system", "Request created.", {})
        return self.get_request(request_id)

    def get_request(self, request_id: int) -> dict[str, Any]:
        with self._lock:
            row = self._conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"Request {request_id} was not found.")
        return dict(row)

    def list_requests(self, status: Optional[str] = None, search: Optional[str] = None) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM requests WHERE 1=1", []
        if status:
            sql += " AND status = ?"
            params.append(status)
        if search:
            like = f"%{search.strip()}%"
            sql += " AND (requester_name LIKE ? OR equipment LIKE ? OR part_description LIKE ? OR part_number LIKE ?)"
            params += [like] * 4
        sql += " ORDER BY id DESC"
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def update_status(self, request_id: int, status: RequestStatus, note: str = "") -> dict[str, Any]:
        old = self.get_request(request_id)
        with self._lock:
            self._conn.execute(
                "UPDATE requests SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, _now(), request_id),
            )
            self._conn.commit()
        summary = f"Status changed from {old['status']} to {status.value}."
        self.add_decision(request_id, "status_change", "operator", summary,
                          {"from": old["status"], "to": status.value, "note": note})
        return self.get_request(request_id)

    def delete_request(self, request_id: int) -> None:
        self.get_request(request_id)
        with self._lock:
            self._conn.execute("DELETE FROM requests WHERE id = ?", (request_id,))
            self._conn.commit()

    # ---------- decisions ----------
    def add_decision(self, request_id: int, kind: str, source: str, summary: str,
                     details: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO decisions (request_id, kind, source, summary, details, created_at) VALUES (?,?,?,?,?,?)",
                (request_id, kind, source, summary, json.dumps(details), _now()),
            )
            self._conn.commit()
            row = self._conn.execute("SELECT * FROM decisions WHERE id = ?", (cur.lastrowid,)).fetchone()
        return self._decision_dict(row)

    def list_decisions(self, request_id: Optional[int] = None, limit: int = 200) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM decisions", []
        if request_id is not None:
            sql += " WHERE request_id = ?"
            params.append(request_id)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [self._decision_dict(r) for r in rows]

    @staticmethod
    def _decision_dict(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["details"] = json.loads(d["details"] or "{}")
        return d

    # ---------- stats ----------
    def stats(self) -> dict[str, int]:
        with self._lock:
            rows = self._conn.execute("SELECT status, COUNT(*) AS c FROM requests GROUP BY status").fetchall()
        counts = {r["status"]: r["c"] for r in rows}
        out = {s.value: counts.get(s.value, 0) for s in RequestStatus}
        out["total"] = sum(out.values())
        return out
