## Nexkosmo alignment contract

### Approved direction
- Alignment manifest version followed:
- Decision/spec implemented:
- `docs/CURRENT_STATE.md` sections affected:
- Does this change canon? If yes, link the Director-approved decision record:

### Canon and data
- Canonical assets/state touched:
- Project-specific fixtures or hard-coded values added/removed:
- If fixtures are used, where are they isolated and labelled?

### Implementation reality
- What is fully implemented?
- What remains placeholder, estimated, inferred, or unknown?
- Does this branch include the current `main` governance/canon changes?

### Development-time verification
- Small verified slices/checks used while coding:
- Failures discovered during implementation and their disposition:
- Latent-defect controls applied where relevant:

### Security by construction
- Security-relevant change? `YES/NO`
- Assets/trust boundaries affected:
- Security invariants applied:
- Threat model required? If yes, link it:
- Abuse/negative security tests run:
- Static/dependency/secret checks run:
- Security findings introduced/resolved:
- Security controls not tested and why:
- Remaining security unknowns:

### Validation
- [ ] `python scripts/verify_canonical_assets.py`
- [ ] `python scripts/verify_alignment.py`
- [ ] `python scripts/verify_drift_guards.py` when significant governance/canon changes apply
- [ ] `python scripts/verify_latent_defect_assurance.py` where high-risk invariants apply
- [ ] `python scripts/verify_authority_model.py` when authority rules are affected
- [ ] `python scripts/verify_security_baseline.py`
- [ ] `python scripts/verify_repo_protection.py` / GitHub reports `main` protected
- [ ] Relevant lint/type/test/integration checks
- [ ] Relevant abuse/negative security tests
- [ ] `quality-and-integration` CI is green
- [ ] Required review/conversation rules match `docs/REPOSITORY_PROTECTION.md`
- [ ] No approved canon changed without explicit Director authority
- [ ] No project-specific fixture is masquerading as production truth
- [ ] No unresolved critical security unknown
- [ ] Documentation and implementation tell the same current story

### Drift / risk check
List any known conflict with current architecture, product direction, data ownership, security, repository protection, or evidence. If none, write `None known`.
