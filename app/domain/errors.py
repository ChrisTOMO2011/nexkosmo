class DomainError(Exception):
    code = "domain_error"


class AuthorizationDenied(DomainError):
    code = "authorization_denied"


class ConcurrencyConflict(DomainError):
    code = "concurrency_conflict"


class InvariantViolation(DomainError):
    code = "invariant_violation"


class IdempotencyConflict(DomainError):
    code = "idempotency_conflict"


class IdempotencyInProgress(DomainError):
    code = "idempotency_in_progress"


class IdempotencyLeaseLost(DomainError):
    code = "idempotency_lease_lost"


class ResourceNotFound(DomainError):
    code = "resource_not_found"


class AuthorityRemediationRequired(DomainError):
    code = "authority_remediation_required"


class ConsentDenied(DomainError):
    code = "consent_denied"
