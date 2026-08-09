from funnel_control.models import FunnelEvent, FunnelStage
from funnel_control.state_machine import FunnelController


def test_lead_is_gated_without_consent():
    controller = FunnelController()
    controller.ingest(FunnelEvent("lead.created", "lead-1", FunnelStage.LEAD, {}))
    assert controller.next_action("lead-1") == "request_or_verify_consent"


def test_consented_lead_can_qualify():
    controller = FunnelController()
    controller.ingest(FunnelEvent(
        "lead.created", "lead-2", FunnelStage.LEAD, {"consented": True}
    ))
    assert controller.next_action("lead-2") == "qualify_lead"
    event = controller.advance("lead-2")
    assert event.stage is FunnelStage.QUALIFIED
    assert controller.next_action("lead-2") == "start_sales_conversation"
