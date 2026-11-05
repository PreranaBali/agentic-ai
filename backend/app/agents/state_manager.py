"""In-memory tracker of agent activity, shown on the Agent Monitor page."""
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any, Optional


class AgentStateManager:
    def __init__(self, max_events: int = 50):
        self._lock = threading.Lock()
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self.runs = 0
        self.failures = 0
        self.last_run_at: Optional[str] = None

    def record(self, request_id: int, ok: bool, groq_used: bool, detail: str) -> None:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._lock:
            self.runs += 1
            if not ok:
                self.failures += 1
            self.last_run_at = now
            self._events.appendleft(
                {"time": now, "request_id": request_id, "ok": ok, "groq_used": groq_used, "detail": detail}
            )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "advisory_runs": self.runs,
                "advisory_failures": self.failures,
                "last_run_at": self.last_run_at,
                "recent_events": list(self._events),
            }
