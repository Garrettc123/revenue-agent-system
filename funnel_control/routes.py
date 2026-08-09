import os
from flask import Blueprint, jsonify, request
from .models import FunnelEvent, FunnelStage
from .state_machine import FunnelController

funnel_bp = Blueprint("funnel_control", __name__, url_prefix="/api/funnel")
controller = FunnelController()


def _authorized() -> bool:
    expected = os.getenv("FUNNEL_CONTROL_SECRET", "")
    if not expected:
        return True
    return request.headers.get("X-Funnel-Secret", "") == expected


@funnel_bp.get("/health")
def funnel_health():
    return jsonify({"status": "healthy", "service": "funnel-control", "trackedLeads": len(controller.states)})


@funnel_bp.post("/events")
def ingest_event():
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    lead_id = payload.get("leadId")
    event_type = payload.get("eventType")
    stage = payload.get("stage")
    data = payload.get("data") or {}

    if not lead_id or not event_type or stage not in {s.value for s in FunnelStage}:
        return jsonify({"error": "leadId, eventType and valid stage are required"}), 400

    event = FunnelEvent(
        event_type=event_type,
        lead_id=lead_id,
        stage=FunnelStage(stage),
        data=data,
    )
    state = controller.ingest(event)
    return jsonify({
        "accepted": True,
        "leadId": state.lead_id,
        "stage": state.stage.value,
        "nextAction": controller.next_action(state.lead_id),
    }), 202


@funnel_bp.get("/leads/<lead_id>")
def lead_state(lead_id: str):
    if not _authorized():
        return jsonify({"error": "unauthorized"}), 401
    state = controller.states.get(lead_id)
    if state is None:
        return jsonify({"error": "lead not found"}), 404
    return jsonify({
        "leadId": state.lead_id,
        "stage": state.stage.value,
        "score": state.score,
        "consented": state.consented,
        "data": state.data,
        "nextAction": controller.next_action(lead_id),
    })
