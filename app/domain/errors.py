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


class ConsentDenied(DomainError):
    code = "consent_denied"
