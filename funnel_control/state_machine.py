from collections.abc import Callable
from .models import FunnelEvent, FunnelStage, LeadState


NEXT_STAGE = {
    FunnelStage.LEAD: FunnelStage.QUALIFIED,
    FunnelStage.QUALIFIED: FunnelStage.ENGAGED,
    FunnelStage.ENGAGED: FunnelStage.OFFERED,
    FunnelStage.OFFERED: FunnelStage.CHECKOUT,
    FunnelStage.CHECKOUT: FunnelStage.CUSTOMER,
    FunnelStage.CUSTOMER: FunnelStage.ONBOARDING,
    FunnelStage.ONBOARDING: FunnelStage.RETAINED,
    FunnelStage.RETAINED: FunnelStage.EXPANSION,
    FunnelStage.EXPANSION: FunnelStage.REFERRAL,
}


class FunnelController:
    """Deterministic funnel state machine with injectable engine adapters."""

    def __init__(self, sales_engine: Callable | None = None, revenue_engine: Callable | None = None):
        self.sales_engine = sales_engine
        self.revenue_engine = revenue_engine
        self.states: dict[str, LeadState] = {}
        self.events: list[FunnelEvent] = []

    def ingest(self, event: FunnelEvent) -> LeadState:
        state = self.states.setdefault(event.lead_id, LeadState(event.lead_id))
        if event.data.get("consented") is not None:
            state.consented = bool(event.data["consented"])
        state.data.update(event.data)
        state.stage = event.stage
        self.events.append(event)
        return state

    def next_action(self, lead_id: str) -> str:
        state = self.states[lead_id]
        if not state.consented and state.stage in {
            FunnelStage.LEAD, FunnelStage.QUALIFIED, FunnelStage.ENGAGED
        }:
            return "request_or_verify_consent"
        return {
            FunnelStage.LEAD: "qualify_lead",
            FunnelStage.QUALIFIED: "start_sales_conversation",
            FunnelStage.ENGAGED: "diagnose_and_present_value",
            FunnelStage.OFFERED: "present_checkout",
            FunnelStage.CHECKOUT: "await_payment_webhook",
            FunnelStage.CUSTOMER: "start_onboarding",
            FunnelStage.ONBOARDING: "verify_value_realization",
            FunnelStage.RETAINED: "evaluate_expansion",
            FunnelStage.EXPANSION: "request_referral",
            FunnelStage.REFERRAL: "attribute_referral",
        }[state.stage]

    def advance(self, lead_id: str, **data) -> FunnelEvent:
        state = self.states[lead_id]
        target = NEXT_STAGE.get(state.stage)
        if target is None:
            raise ValueError(f"No next stage for {state.stage}")
        event = FunnelEvent(
            event_type=f"funnel.{target.value}",
            lead_id=lead_id,
            stage=target,
            data=data,
        )
        self.ingest(event)
        return event
