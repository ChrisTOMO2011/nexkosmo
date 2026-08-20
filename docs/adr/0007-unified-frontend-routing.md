# ADR 0007: Unified frontend routing

Status: accepted.

The cinematic landing and React Studio share one deployment and origin. `/`
serves the landing; `/studio` and `/studio/*` resolve through the React entry.
Project/Character context travels through routes or explicit query parameters.
There is no iframe or hard-coded second frontend host.
