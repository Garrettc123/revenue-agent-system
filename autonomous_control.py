"""Production control plane for the autonomous revenue runtime."""
from __future__ import annotations

import os
from flask import Blueprint, jsonify, request

from autonomous_runtime import get_runtime
from master_conductor import get_conductor

agents_bp = Blueprint("autonomous_agents", __name__, url_prefix="/api/agents")


def _runtime():
    conductor = get_conductor()

    def revenue_reader():
        dashboard = conductor.get_master_dashboard()
        summary = dashboard.get("summary", {})
        return {
            "configured": True,
            "mrr": summary.get("totalMonthlyRevenue", 0),
            "customers": summary.get("activeCustomers", 0),
            "arr": summary.get("totalYearlyProjection", 0),
            "total_revenue": summary.get("totalMonthlyRevenue", 0),
            "source": "master_conductor_dashboard",
        }

    return get_runtime(conductor=conductor, revenue_reader=revenue_reader)


def _authorized() -> bool:
    expected = os.getenv("AGENTS_CONTROL_SECRET", "")
    if not expected:
        return True
    return request.headers.get("X-Agents-Secret", "") == expected


@agents_bp.get("/status")
def status():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(_runtime().status())


@agents_bp.get("/health")
def health():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    runtime = _runtime()
    return jsonify({
        "status": "healthy",
        "running": runtime.running,
        "cycle_count": runtime.cycle_count,
        "interval_seconds": runtime.interval,
        "ledger": str(runtime.ledger.path),
    })


@agents_bp.post("/start")
def start():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(_runtime().start())


@agents_bp.post("/stop")
def stop():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(_runtime().stop())


@agents_bp.post("/force-cycle")
def force_cycle():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(_runtime().force_cycle())


@agents_bp.get("/events")
def events():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        limit = 50
    return jsonify({"events": _runtime().ledger.recent(limit)})
