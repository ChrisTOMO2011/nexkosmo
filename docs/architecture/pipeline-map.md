# Pipeline map

| Stage | Status |
|---|---|
| Pre-Production / Character Identity | Phase 3 development-ready: canonical PostgreSQL persistence, compatible assets and package readiness |
| Pre-Production / Environment | Phase 4A development-ready: canonical Production-owned package, compatible selections and honest structured readiness |
| Script | deferred boundary only |
| Set | layout scaffold only; product work deferred |
| Studio | layout scaffold only; product work deferred |
| Render | layout scaffold only; product work deferred |
| Review | missing/deferred |

All navigation uses the unified frontend origin. CGI and VFX labels may navigate
to a Studio editor context, but no CGI/VFX editor capability is activated by this
phase. Character mutations invalidate downstream Set, Studio, Review and Render
dependency state; no downstream consumer is registered yet.

Environment packages are future Scene inputs. Scene Builder must store an
`environment_id` reference and inherit canonical package state rather than duplicate
it. Preview assembly is deferred, so a fully selected package may correctly remain
`processing_required` and cannot advance to Set.
