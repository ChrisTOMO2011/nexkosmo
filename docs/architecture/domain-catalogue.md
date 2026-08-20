# Domain catalogue

| Domain | Status | Canonical objects |
|---|---|---|
| Workspace and membership | implemented | workspace rows, project membership roles, RLS context |
| Project | implemented | immutable aggregate, optimistic version, membership operations |
| Production | implemented | immutable aggregate owned by Project and Workspace |
| Character | development-ready | one immutable aggregate projected through Identity, Face, Hair, Skin, Eyes, Beard, Age and Expression; species capabilities, style profiles, compatible manifests, accessories, package readiness and downstream status |
| Environment | development-ready | immutable Production-owned Environment package, canonical type/capability registry, compatible asset selections, constraints and structured readiness |
| Identity/assertion/decision/policy semantic kernel | partial/deferred | domain types and ports exist; runtime repositories are not wired |
| Script, Scene, generated media, VFX/CGI and rendering | missing/deferred | not part of the current product foundation |

Identifiers are UUIDs. Filenames and display names are never canonical identity.
Character editor tabs are category projections over the Character aggregate and the
shared asset-manifest catalogue; they are not separate character records or stores.
Environment editor tabs follow the same presentation rule while retaining a separate,
strongly typed controller, application service, repository and compatibility policy.
