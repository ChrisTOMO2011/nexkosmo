# Event Contracts

Increment 1 registers the event envelope persistence shape:

- event ID
- workspace ID
- aggregate ID
- aggregate sequence
- event type
- event version
- payload
- occurrence and availability time
- lease and delivery state

Initial contract names:

- `kernel.assertion.recorded` v1
- `kernel.decision.recorded` v1

Event payload schemas and compatibility tests remain blocking for Increment 2.
