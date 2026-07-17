import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.application.ports import AuditPort, IdempotencyPort, UnitOfWorkFactory
from app.domain.belief import resolve_belief
from app.domain.contradiction import detect_literal_conflicts
from app.domain.rules import (
    authorize_by_policies,
    require_human_authority,
    require_workspace,
    validate_assertion,
)
from app.domain.types import Assertion, Decision, Principal


class SemanticKernelService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        audit: AuditPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._audit = audit
        self._idempotency = idempotency

    async def record_assertion(
        self,
        principal: Principal,
        assertion: Assertion,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        require_workspace(principal, assertion.workspace_id)
        validate_assertion(assertion)
        request_hash = self._hash({"assertion_id": str(assertion.id)})
        await self._idempotency.acquire(
            assertion.workspace_id, idempotency_key, request_hash
        )
        try:
            async with self._uow_factory(principal) as uow:
                await uow.registry.require_active(
                    "predicate", assertion.predicate, 1
                )
                await uow.assertions.add(assertion)
                await uow.outbox.append(
                    "kernel.assertion.recorded",
                    1,
                    {
                        "assertion_id": str(assertion.id),
                        "workspace_id": str(assertion.workspace_id),
                    },
                )
                await uow.commit()
            response = {"assertion_id": str(assertion.id)}
            await self._idempotency.complete(
                assertion.workspace_id, idempotency_key, response
            )
            await self._audit.record_independent(
                principal=principal,
                action="assertion.record",
                outcome="success",
                resource_id=assertion.id,
                details={},
            )
            return response
        except Exception as exc:
            await self._idempotency.fail(
                assertion.workspace_id,
                idempotency_key,
                getattr(exc, "code", "internal_error"),
            )
            await self._audit.record_independent(
                principal=principal,
                action="assertion.record",
                outcome="failure",
                resource_id=assertion.id,
                details={"error": getattr(exc, "code", type(exc).__name__)},
            )
            raise

    async def decide(
        self,
        principal: Principal,
        decision: Decision,
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        require_workspace(principal, decision.workspace_id)
        require_human_authority(principal, "knowledge.decide")
        request_hash = self._hash({"decision_id": str(decision.id)})
        await self._idempotency.acquire(
            decision.workspace_id, idempotency_key, request_hash
        )
        try:
            async with self._uow_factory(principal) as uow:
                await uow.decisions.add(decision)
                await uow.outbox.append(
                    "kernel.decision.recorded",
                    1,
                    {
                        "decision_id": str(decision.id),
                        "outcome": decision.outcome.value,
                    },
                )
                await uow.commit()
            response = {"decision_id": str(decision.id)}
            await self._idempotency.complete(
                decision.workspace_id, idempotency_key, response
            )
            await self._audit.record_independent(
                principal=principal,
                action="knowledge.decide",
                outcome="success",
                resource_id=decision.id,
                details={"outcome": decision.outcome.value},
            )
            return response
        except Exception as exc:
            await self._idempotency.fail(
                decision.workspace_id,
                idempotency_key,
                getattr(exc, "code", "internal_error"),
            )
            await self._audit.record_independent(
                principal=principal,
                action="knowledge.decide",
                outcome="failure",
                resource_id=decision.id,
                details={"error": getattr(exc, "code", type(exc).__name__)},
            )
            raise

    async def resolve(
        self,
        principal: Principal,
        *,
        subject_id: UUID,
        context_id: UUID,
    ) -> dict[str, Any]:
        async with self._uow_factory(principal) as uow:
            policies = await uow.policies.list_for_request(
                agent_id=principal.agent_id,
                resource_id=subject_id,
            )
            authorize_by_policies(
                policies,
                agent_id=principal.agent_id,
                resource_id=subject_id,
                context_id=context_id,
                action="knowledge.read",
                purpose="belief_resolution",
                at=datetime.now(UTC),
            )
            assertions = await uow.assertions.list_for_subject(
                subject_id, context_id
            )
            decisions = await uow.decisions.list_for_targets(
                tuple(a.id for a in assertions)
            )
            contradictions = detect_literal_conflicts(assertions)
            resolution = resolve_belief(assertions, decisions)
            return {
                "accepted": [str(x) for x in resolution.accepted],
                "rejected": [str(x) for x in resolution.rejected],
                "proposed": [str(x) for x in resolution.proposed],
                "contradictions": [
                    {
                        "left": str(c.left_assertion_id),
                        "right": str(c.right_assertion_id),
                        "reason": c.reason,
                    }
                    for c in contradictions
                ],
                "decision_ids": [str(x) for x in resolution.decision_ids],
                "explanation": list(resolution.explanation),
            }

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()
