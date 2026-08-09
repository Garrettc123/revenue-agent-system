from funnel_control.integration import build_funnel_event


def test_build_funnel_event():
    event = build_funnel_event("lead-1", "qualified", "sales.qualification", {"score": 0.8})
    assert event["lead_id"] == "lead-1"
    assert event["stage"] == "qualified"
    assert event["data"]["score"] == 0.8
