from enum import StrEnum


class AgentKind(StrEnum):
    HUMAN = "human"
    AI = "ai"
    SERVICE = "service"
    ORGANIZATION = "organization"


class IdentityKind(StrEnum):
    AGENT = "agent"
    CHARACTER = "character"
    PROJECT = "project"
    CONTEXT = "context"
    EVIDENCE = "evidence"
    MODEL = "model"
    POLICY = "policy"
    CREATIVE_WORK = "creative_work"


class ContextKind(StrEnum):
    WORKSPACE = "workspace"
    PROJECT = "project"
    UNIVERSE = "universe"
    DRAFT = "draft"
    CANON = "canon"


class EpistemicStatus(StrEnum):
    OBSERVED = "observed"
    AUTHORED = "authored"
    INFERRED = "inferred"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    WITHDRAWN = "withdrawn"
    UNKNOWN = "unknown"


class DecisionOutcome(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    ESCALATE = "escalate"
    WITHDRAW = "withdraw"


class PolicyEffect(StrEnum):
    PERMIT = "permit"
    PROHIBIT = "prohibit"
    DUTY = "duty"


class AssertionObjectKind(StrEnum):
    IDENTITY = "identity"
    LITERAL = "literal"
