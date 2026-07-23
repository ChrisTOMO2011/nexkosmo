from datetime import datetime
from uuid import UUID

from app.domain.enums import AgentKind, EpistemicStatus, PolicyEffect
from app.domain.errors import AuthorizationDenied, InvariantViolation
from app.domain.types import Assertion, Policy, Principal


def require_workspace(principal: Principal, workspace_id: UUID) -> None:
    if principal.workspace_id != workspace_id and workspace_id not in principal.memberships:
        raise AuthorizationDenied("Principal is not a member of the workspace.")


def require_human_authority(principal: Principal, action: str) -> None:
    if principal.agent_kind is not AgentKind.HUMAN:
        raise AuthorizationDenied("This decision requires human authority.")
    if action not in principal.delegated_actions and "*" not in principal.delegated_actions:
        raise AuthorizationDenied(f"Principal lacks delegated action: {action}")


def validate_assertion(assertion: Assertion) -> None:
    if assertion.object_identity_id is None and assertion.object_value is None:
        raise InvariantViolation("Assertion requires an identity object or literal value.")
    if assertion.object_identity_id is not None and assertion.object_value is not None:
        raise InvariantViolation("Assertion cannot have both identity and literal objects.")
    if assertion.valid_from and assertion.valid_to and assertion.valid_to <= assertion.valid_from:
        raise InvariantViolation("valid_to must be later than valid_from.")
    if assertion.epistemic_status is EpistemicStatus.ACCEPTED:
        raise InvariantViolation(
            "Assertions are not created as accepted; acceptance requires a Decision."
        )


def policy_applies(
    policy: Policy,
    *,
    agent_id: UUID,
    resource_id: UUID,
    context_id: UUID,
    action: str,
    purpose: str,
    at: datetime,
) -> bool:
    if policy.subject_agent_id != agent_id:
        return False
    if policy.resource_identity_id != resource_id:
        return False
    if policy.context_id != context_id:
        return False
    if policy.action != action or policy.purpose != purpose:
        return False
    if at < policy.valid_from:
        return False
    if policy.valid_to is not None and at >= policy.valid_to:
        return False
    return True


def authorize_by_policies(
    policies: list[Policy],
    *,
    agent_id: UUID,
    resource_id: UUID,
    context_id: UUID,
    action: str,
    purpose: str,
    at: datetime,
) -> None:
    applicable = [
        policy
        for policy in policies
        if policy_applies(
            policy,
            agent_id=agent_id,
            resource_id=resource_id,
            context_id=context_id,
            action=action,
            purpose=purpose,
            at=at,
        )
    ]
    if any(p.effect is PolicyEffect.PROHIBIT for p in applicable):
        raise AuthorizationDenied("An explicit prohibition applies.")
    if not any(p.effect is PolicyEffect.PERMIT for p in applicable):
        raise AuthorizationDenied("No applicable permission exists.")
