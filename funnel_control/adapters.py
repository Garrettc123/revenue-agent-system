from typing import Any, Protocol


class SalesEngine(Protocol):
    def handle_lead(self, lead: dict[str, Any]) -> dict[str, Any]: ...


class RevenueEngine(Protocol):
    def handle_event(self, event: dict[str, Any]) -> dict[str, Any]: ...


class SalesAdapter:
    def __init__(self, engine: SalesEngine):
        self.engine = engine

    def qualify(self, lead: dict[str, Any]) -> dict[str, Any]:
        return self.engine.handle_lead(lead)


class RevenueAdapter:
    def __init__(self, engine: RevenueEngine):
        self.engine = engine

    def dispatch(self, event: dict[str, Any]) -> dict[str, Any]:
        return self.engine.handle_event(event)
