# Shared Pre-Production workspace foundation

## Status

The Character Identity page is the canonical presentation template for future
Pre-Production domains. This extraction does not activate Environment, Camera
Gear, Lighting, Audio, VFX, Props, or Vehicles.

## Ownership boundary

The shared components are presentation-only. They receive typed view data,
React content, and callbacks. They do not own persistence, compatibility,
validation, API access, optimistic concurrency, idempotency, audit delivery,
outbox events, or tenant policy.

Every domain must retain its own strongly typed controller and API client. The
canonical backend remains PostgreSQL through repositories, unit of work,
application services, and FastAPI.

## Canonical composition

`PreProductionWorkspace` preserves the Character page's existing DOM regions:

1. `workspace-top`
   - `DomainSourcePanel`
   - `DomainPreviewCarousel`
   - `DomainSelectionRail`
2. `lower-editor`
   - `DomainEditorTabs`
   - `DomainEditorContent`
3. The existing `StudioLayout` continues to provide navigation, sidebars,
   inspector placement, bottom actions, and status messaging.

Reusable catalogue and inspector components are:

- `DomainAssetGrid`
- `AssetSelectionSection`
- `CategorisedAssetSection`
- `FilterPills`
- `ActionCards`
- `DomainInspectorPanel`
- `SuggestionsPanel`
- `DomainStatusNotice`
- `DeferredActionNotice`
- `ActiveProducerPanel`

Character components remain typed adapters around these shared components.
Character state, mutations, compatibility handling, conflict recovery, and API
mapping remain in the Character feature.

Shared presentation types describe domain identifiers, tab presentation, asset
card status and producer-panel context. They are not domain objects and must not
be used as a universal controller or persistence model.

## Selection-state contract

Mutually exclusive controls use one purple active border and `aria-pressed`.
They do not render a second circular checkmark. This applies to identity
variants, visual style, species, Face, Hair, Skin, Eyes, Beard, Age and
Expression.

Multi-select collections use a checkmark to communicate collection membership.
They do not reuse the single-choice `is-selected` border. Keyboard focus remains
the global two-pixel focus outline, so focus and membership are distinguishable.

Asset cards expose one of `available`, `unsupported`, `deferred`, `uploading`,
`generating`, `processing` or `failed`. Unsupported cards are disabled with an
explanatory title. Deferred action cards remain operable so they can explain the
phase boundary, but they cannot create local or durable fake results.

## Deferred actions

Character upload and AI-generation controls retain their approved location and
styling. Activating them produces an accessible warning notice. No browser-local
asset preview, upload row, generation job, success message or fabricated result
is created.

Curated Character suggestions are labelled as curated presets. Until a preset
is mapped to a real Character command and compatibility rule, Apply reports the
deferred boundary and does not toggle a fake applied state.

## Active producer contract

`ActiveProducerPanel` accepts a typed producer profile and current domain
context. It replaces the lower-left Copilot card without changing its geometry.
The Project API client can read an optional assigned profile when the canonical
API eventually supplies it. The current backend has no producer/director field,
so the honest fallback is `AI Producer` / `Producer not assigned`.

Producer activation is deferred. Clicking the action does not start a chat,
create a thread, invoke Semantic Kernel or contact a model provider.

## Visual contract

The extraction deliberately preserves the established Character class names,
element ordering, accessibility attributes, and responsive CSS. The
`character-identity` Studio variant remains the approved visual contract and is
not replaced by generic dimensions.

Future domains must use the same workspace composition while supplying their
own content, typed controller, inspector form, asset projections, and backend
commands. New domain implementation requires its own approved content and must
not alter the Character baseline.

## Accepted catalogue projection behavior

The shared presentation layer does not infer catalogue fallbacks. A domain controller
must provide each category's items explicitly; an intentionally empty category remains
empty apart from the shared deferred action cards. Character maps its approved display
labels to canonical manifest subcategories at the typed adapter boundary.

Species filter pills are presentation state. Selecting Human, Elf, Orc, Robot, Dragon
or Alien changes the visible catalogue projection only and never issues a Character
mutation. All exposes the primary enabled set and More exposes enabled species outside
that set. A Character mutation occurs only when the user activates a species card.

## Environment implementation

Environment is the second typed domain controller using the shared presentation
foundation. It supplies Environment-specific source, preview, package rail, editor
tabs, compatible asset projections, inspector fields, curated suggestions and status
messages without moving compatibility or persistence rules into shared React code.

Its category and subcategory filters query the canonical Environment manifest
projection. Filter changes are non-mutating; asset activation performs the explicit
single- or multi-select backend command. Upload, generation and producer controls
remain honest deferred actions and create no files, jobs, assets or conversations.
