"""Integration helpers for the revenue application's funnel control plane."""

from typing import Any


def build_funnel_event(lead_id: str, stage: str, event_type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "lead_id": lead_id,
        "stage": stage,
        "data": data or {},
    }
