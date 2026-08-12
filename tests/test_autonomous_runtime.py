import tempfile
from pathlib import Path

from autonomous_runtime import AutonomousRuntime, EventLedger


def test_runtime_force_cycle_creates_auditable_events():
    with tempfile.TemporaryDirectory() as tmp:
        ledger = EventLedger(Path(tmp) / "runtime.sqlite3")
        runtime = AutonomousRuntime(
            revenue_reader=lambda: {
                "configured": True,
                "mrr": 2500,
                "customers": 10,
                "arr": 30000,
                "total_revenue": 5000,
            },
            interval=90,
        )
        runtime.ledger = ledger
        result = runtime.force_cycle()
        assert result["status"] == "completed"
        assert result["cycle_count"] == 1
        assert result["opportunities"]
        events = ledger.recent(50)
        assert any(e["event_type"] == "revenue_snapshot" for e in events)
        assert any(e["event_type"] == "cycle_completed" for e in events)


def test_runtime_is_bounded_and_exposes_expected_agents():
    runtime = AutonomousRuntime(revenue_reader=lambda: {"configured": True, "mrr": 0, "customers": 0})
    assert runtime.interval >= 10
    assert {"DealCloser", "PricingDynamo", "LeadNurtureBot", "CheckoutOptimizer", "RetentionEngine"}.issubset(set(runtime.AGENTS))
