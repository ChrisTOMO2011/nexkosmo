# Registry Specification

Registry entries govern:

- identity kinds
- agent kinds
- context kinds
- assertion predicates
- epistemic statuses
- evidence relations
- activity types
- policy actions and purposes
- decision types
- event contracts

A registry definition is immutable by `(workspace, namespace, key, version)`.
Semantic change requires a new version and compatibility declaration.

## Evidence terminology boundary

Permanent Semantic Kernel epistemic statuses describe the state or basis of assertions and knowledge records, for example `OBSERVED`, `AUTHORED`, `INFERRED`, `PROPOSED`, `ACCEPTED`, `REJECTED`, `DISPUTED`, `WITHDRAWN`, and `UNKNOWN`.

Agent reporting confidence is a separate concern and must not redefine those kernel statuses. Repository agents use `SUSPECTED`, `SUPPORTED`, `STRONGLY_SUPPORTED`, and `VERIFIED` as claim-confidence labels, with contradiction state reported separately.

This separation prevents a reporting convention from silently becoming a competing semantic truth model.
