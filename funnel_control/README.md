# Funnel Control Plane

A deterministic orchestration layer for the Garcar revenue stack.

## Responsibilities

- Maintain a canonical lead/customer funnel state.
- Consume sales and payment lifecycle events.
- Decide the next permitted funnel action.
- Keep sales and revenue engines behind explicit adapters.
- Preserve consent state and an auditable event trail.

## Integration contract

The control plane does not assume the internal implementation of either engine. Inject adapters implementing:

- `SalesEngine.handle_lead(lead)`
- `RevenueEngine.handle_event(event)`

This keeps orchestration independent from individual application layouts and prevents duplicate business logic.

## Safety boundaries

The controller never invents consent, payment success, customer identity, or revenue. External systems must provide authoritative events. Outreach automation should remain subject to applicable consent, opt-out, and platform policies.
