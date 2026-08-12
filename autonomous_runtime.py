"""Persistent autonomous revenue runtime.

The runtime is deliberately capability-driven: it can observe real revenue data,
produce prioritized opportunities, and execute only registered actions. External
side effects must be supplied as explicit action handlers, which keeps the core
loop auditable and idempotent.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = int(os.getenv("AUTONOMOUS_RUNTIME_INTERVAL", "90"))
DB_PATH = Path(os.getenv("AUTONOMOUS_RUNTIME_DB", "/tmp/garcar_revenue_runtime.sqlite3"))


class EventLedger:
    """Small durable ledger used for observability and idempotency."""

    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS revenue_events (
                id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                event_key TEXT NOT NULL UNIQUE,
                agent TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_events_created ON revenue_events(created_at DESC)")
            db.execute("""CREATE TABLE IF NOT EXISTS runtime_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )""")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def claim_event(self, event_key: str) -> bool:
        with self._lock, self._connect() as db:
            try:
                db.execute(
                    "INSERT INTO revenue_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), "pending", event_key, "runtime", "claim", "claimed", "{}", _now()),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def write(self, cycle_id: str, agent: str, event_type: str, payload: dict[str, Any], *, event_key: str | None = None, status: str = "completed") -> dict[str, Any]:
        key = event_key or _event_key(cycle_id, agent, event_type, payload)
        record = {
            "id": str(uuid.uuid4()), "cycle_id": cycle_id, "event_key": key,
            "agent": agent, "event_type": event_type, "status": status,
            "payload": payload, "created_at": _now(),
        }
        with self._lock, self._connect() as db:
            try:
                db.execute(
                    "INSERT INTO revenue_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (record["id"], cycle_id, key, agent, event_type, status, json.dumps(payload, default=str), record["created_at"]),
                )
            except sqlite3.IntegrityError:
                row = db.execute("SELECT * FROM revenue_events WHERE event_key=?", (key,)).fetchone()
                if row:
                    record = dict(row)
                    record["payload"] = json.loads(record["payload"])
        return record

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM revenue_events ORDER BY created_at DESC LIMIT ?", (max(1, min(limit, 200)),)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try: item["payload"] = json.loads(item["payload"])
            except Exception: pass
            result.append(item)
        return result

    def state(self) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT key,value FROM runtime_state").fetchall()
        return {r["key"]: json.loads(r["value"]) for r in rows}

    def set_state(self, key: str, value: Any) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT OR REPLACE INTO runtime_state(key,value) VALUES (?,?)", (key, json.dumps(value, default=str)))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event_key(cycle_id: str, agent: str, event_type: str, payload: dict[str, Any]) -> str:
    raw = json.dumps([cycle_id, agent, event_type, payload], sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


class AutonomousRuntime:
    """90-second control loop for observable, bounded revenue operations."""

    AGENTS = (
        "DealCloser", "PricingDynamo", "DynamicPricingAI", "LeadNurtureBot",
        "CheckoutOptimizer", "AdRevenueOptimizer", "RetentionEngine",
        "RevenueSentinel", "OpportunityRanker", "ExperimentEngine",
    )

    def __init__(self, conductor: Any = None, revenue_reader: Callable[[], dict[str, Any]] | None = None, interval: int = DEFAULT_INTERVAL) -> None:
        self.conductor = conductor
        self.revenue_reader = revenue_reader
        self.interval = max(10, interval)
        self.ledger = EventLedger()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._cycle_lock = threading.Lock()
        self.cycle_count = int(self.ledger.state().get("cycle_count", 0))
        self.last_cycle: dict[str, Any] | None = self.ledger.state().get("last_cycle")

    @property
    def running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def start(self) -> dict[str, Any]:
        if self.running:
            return self.status()
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="autonomous-revenue-runtime", daemon=True)
        self._thread.start()
        self.ledger.set_state("started_at", _now())
        return self.status()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=3)
        return self.status()

    def force_cycle(self) -> dict[str, Any]:
        return self.run_cycle(trigger="manual")

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "interval_seconds": self.interval,
            "cycle_count": self.cycle_count,
            "last_cycle": self.last_cycle,
            "agents": [{"name": a, "status": "active" if self.running else "standby"} for a in self.AGENTS],
            "ledger": str(self.ledger.path),
        }

    def _loop(self) -> None:
        # Run once immediately, then every interval. This makes deployment observable
        # without waiting 90 seconds, while stop remains responsive.
        try:
            self.run_cycle(trigger="startup")
        except Exception:
            logger.exception("Autonomous runtime startup cycle failed")
        while not self._stop.wait(self.interval):
            try:
                self.run_cycle(trigger="scheduled")
            except Exception:
                logger.exception("Autonomous runtime scheduled cycle failed")

    def run_cycle(self, trigger: str = "scheduled") -> dict[str, Any]:
        if not self._cycle_lock.acquire(blocking=False):
            return {"status": "busy"}
        try:
            cycle_id = f"cycle-{int(time.time())}-{uuid.uuid4().hex[:8]}"
            started = time.monotonic()
            self.cycle_count += 1
            self.ledger.set_state("cycle_count", self.cycle_count)
            revenue = self._read_revenue()
            snapshot = self._snapshot(revenue)
            self._emit(cycle_id, "RevenueSentinel", "revenue_snapshot", snapshot)

            opportunities = self._rank_opportunities(revenue)
            self._emit(cycle_id, "OpportunityRanker", "opportunities_ranked", {"count": len(opportunities), "items": opportunities})

            actions = self._plan_actions(opportunities, revenue)
            for action in actions:
                self._emit(cycle_id, action["agent"], action["type"], action["payload"])

            if self.conductor:
                try:
                    health = self.conductor.get_system_health()
                    self._emit(cycle_id, "RevenueSentinel", "system_health", health)
                except Exception as exc:
                    self._emit(cycle_id, "RevenueSentinel", "health_error", {"error": str(exc)}, status="error")

            result = {
                "status": "completed", "cycle_id": cycle_id, "trigger": trigger,
                "cycle_count": self.cycle_count, "duration_ms": round((time.monotonic() - started) * 1000, 2),
                "revenue": revenue, "opportunities": opportunities, "actions": actions,
                "timestamp": _now(),
            }
            self.last_cycle = result
            self.ledger.set_state("last_cycle", result)
            self._emit(cycle_id, "AutonomousRuntime", "cycle_completed", {"trigger": trigger, "duration_ms": result["duration_ms"], "opportunities": len(opportunities), "actions": len(actions)})
            return result
        finally:
            self._cycle_lock.release()

    def _read_revenue(self) -> dict[str, Any]:
        if self.revenue_reader:
            return dict(self.revenue_reader())
        return {"configured": False, "mrr": 0, "customers": 0, "arr": 0, "total_revenue": 0}

    @staticmethod
    def _snapshot(revenue: dict[str, Any]) -> dict[str, Any]:
        return {k: revenue.get(k) for k in ("configured", "mrr", "customers", "arr", "total_revenue")}

    def _rank_opportunities(self, revenue: dict[str, Any]) -> list[dict[str, Any]]:
        customers = int(revenue.get("customers") or 0)
        mrr = float(revenue.get("mrr") or 0)
        opportunities: list[dict[str, Any]] = []
        if not revenue.get("configured"):
            opportunities.append({"score": 100, "type": "configuration", "reason": "Stripe revenue source is not configured"})
        if customers == 0:
            opportunities.append({"score": 98, "type": "acquisition", "reason": "No verified active customers"})
        elif mrr / max(customers, 1) < 100:
            opportunities.append({"score": 90, "type": "expansion", "reason": "Revenue per customer is below $100 MRR"})
        opportunities.append({"score": 75, "type": "checkout", "reason": "Optimize the path from qualified intent to checkout"})
        opportunities.append({"score": 70, "type": "retention", "reason": "Run retention and reactivation analysis"})
        return sorted(opportunities, key=lambda x: x["score"], reverse=True)

    def _plan_actions(self, opportunities: list[dict[str, Any]], revenue: dict[str, Any]) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        mapping = {
            "configuration": ("RevenueSentinel", "configuration_alert"),
            "acquisition": ("LeadNurtureBot", "acquisition_gap"),
            "expansion": ("DynamicPricingAI", "expansion_candidate"),
            "checkout": ("CheckoutOptimizer", "checkout_experiment"),
            "retention": ("RetentionEngine", "retention_pass"),
        }
        for opportunity in opportunities[:5]:
            agent, event_type = mapping[opportunity["type"]]
            actions.append({"agent": agent, "type": event_type, "payload": {"opportunity": opportunity, "revenue_snapshot": self._snapshot(revenue)}})
        return actions

    def _emit(self, cycle_id: str, agent: str, event_type: str, payload: dict[str, Any], status: str = "completed") -> None:
        self.ledger.write(cycle_id, agent, event_type, payload, status=status)


_runtime: AutonomousRuntime | None = None
_runtime_lock = threading.Lock()


def get_runtime(conductor: Any = None, revenue_reader: Callable[[], dict[str, Any]] | None = None) -> AutonomousRuntime:
    global _runtime
    with _runtime_lock:
        if _runtime is None:
            _runtime = AutonomousRuntime(conductor=conductor, revenue_reader=revenue_reader)
        return _runtime
