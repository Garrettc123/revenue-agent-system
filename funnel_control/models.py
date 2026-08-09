from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FunnelStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    ENGAGED = "engaged"
    OFFERED = "offered"
    CHECKOUT = "checkout"
    CUSTOMER = "customer"
    ONBOARDING = "onboarding"
    RETAINED = "retained"
    EXPANSION = "expansion"
    REFERRAL = "referral"


@dataclass
class FunnelEvent:
    event_type: str
    lead_id: str
    stage: FunnelStage
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class LeadState:
    lead_id: str
    stage: FunnelStage = FunnelStage.LEAD
    score: float = 0.0
    consented: bool = False
    data: dict[str, Any] = field(default_factory=dict)
