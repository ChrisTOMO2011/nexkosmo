# Nexkosmo Asset Inbox

Drop new, unregistered source assets into this directory. The Brain must inspect each item, detect its canonical domain and identity hierarchy, create the required library folders, preserve the original source, register metadata and provenance, and then move the asset into its canonical destination.

## Intake folders

- `humans/` — optional pre-hint for human assets
- `creatures/` — optional pre-hint for supernatural or fictional creatures
- `animals/` — optional pre-hint for real-world animals
- `vehicles/` — optional pre-hint for vehicles
- `environments/` — optional pre-hint for locations and environments
- `audio/` — optional pre-hint for sound assets
- `video/` — optional pre-hint for footage and animation
- `documents/` — optional pre-hint for scripts, briefs, specifications and reference documents
- `mixed/` — sheets or packages containing multiple asset types
- `unclassified/` — default drop location when no hint is supplied
- `needs-review/` — assets the Brain cannot classify with sufficient confidence

Folder placement is only a hint. The Brain's detection result remains authoritative. Assets must never be moved directly into the canonical library without registration, provenance capture and verification.
