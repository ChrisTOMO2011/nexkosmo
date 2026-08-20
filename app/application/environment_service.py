from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.application.environment_compatibility import EnvironmentCompatibilityService
from app.application.ports import AuditDeliveryPort, IdempotencyPort, UnitOfWork, UnitOfWorkFactory
from app.application.project_service import EDIT_ROLES, READ_ROLES, require_project_role
from app.domain.environments import (
    ENVIRONMENT_COLLECTION_SELECTIONS,
    Environment,
    EnvironmentAssetManifest,
    EnvironmentLocationType,
    EnvironmentReadiness,
    EnvironmentType,
    InteriorExterior,
)
from app.domain.errors import ConcurrencyConflict, InvariantViolation, NotFound
from app.domain.rules import require_workspace
from app.domain.types import Principal


@dataclass(frozen=True, slots=True)
class EnvironmentMutationResult:
    environment: Environment
    change_summary: dict[str, Any]
    replayed_response: dict[str, Any] | None = None


EnvironmentTransform = Callable[
    [UnitOfWork, Environment], Awaitable[tuple[Environment, dict[str, Any]]]
]


class EnvironmentApplicationService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        audit: AuditDeliveryPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._audit = audit
        self._idempotency = idempotency

    async def create_environment(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        production_id: UUID,
        display_name: str,
        environment_type_id: UUID,
        description: str,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        action = "environment.created"
        request_hash = self._hash(
            {
                "operation": action,
                "project_id": str(project_id),
                "production_id": str(production_id),
                "display_name": display_name,
                "environment_type_id": str(environment_type_id),
                "description": description,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            replayed_environment = await self.get_environment(
                principal, UUID(claim.response["environment"]["environment_id"])
            )
            return EnvironmentMutationResult(replayed_environment, {}, claim.response)
        environment: Environment | None = None
        try:
            async with self._uow_factory(principal) as uow:
                await require_project_role(uow, principal, project_id, EDIT_ROLES)
                production = await uow.productions.get_by_id(production_id)
                if (
                    production is None
                    or production.project_id != project_id
                    or production.workspace_id != principal.workspace_id
                ):
                    raise NotFound("Production does not belong to the selected project.")
                environment_type = await self._require_type(uow, environment_type_id)
                environment = Environment.create(
                    workspace_id=principal.workspace_id,
                    project_id=project_id,
                    production_id=production_id,
                    display_name=display_name,
                    description=description,
                    environment_type_id=environment_type.environment_type_id,
                )
                await uow.environments.add(environment)
                summary = {"environment_type_id": str(environment_type_id)}
                await uow.outbox.append(
                    action,
                    1,
                    self._event_payload(environment, previous_version=0, summary=summary),
                    aggregate_id=environment.environment_id,
                    aggregate_sequence=environment.version,
                )
                response = self._mutation_response(environment, summary)
                await uow.idempotency.complete(idempotency_key, response)
                await self._queue_audit_success(
                    uow,
                    principal,
                    environment,
                    idempotency_key=idempotency_key,
                    action=action,
                    previous_version=0,
                    summary=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action=action)
            return EnvironmentMutationResult(environment, summary)
        except Exception as exc:
            await self._mutation_failure(
                principal,
                idempotency_key,
                action,
                environment.environment_id if environment else None,
                exc,
            )
            raise

    async def get_environment(self, principal: Principal, environment_id: UUID) -> Environment:
        async with self._uow_factory(principal) as uow:
            environment = await self._require_environment(uow, environment_id)
            require_workspace(principal, environment.workspace_id)
            await require_project_role(uow, principal, environment.project_id, READ_ROLES)
            return environment

    async def create_production_environment(
        self,
        principal: Principal,
        *,
        production_id: UUID,
        display_name: str,
        environment_type_id: UUID,
        description: str,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        async with self._uow_factory(principal) as uow:
            production = await uow.productions.get_by_id(production_id)
            if production is None:
                raise NotFound("Production does not exist.")
            await require_project_role(uow, principal, production.project_id, EDIT_ROLES)
            project_id = production.project_id
        return await self.create_environment(
            principal,
            project_id=project_id,
            production_id=production_id,
            display_name=display_name,
            environment_type_id=environment_type_id,
            description=description,
            idempotency_key=idempotency_key,
        )

    async def list_project_environments(
        self, principal: Principal, project_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        async with self._uow_factory(principal) as uow:
            await require_project_role(uow, principal, project_id, READ_ROLES)
            return await uow.environments.list_by_project(project_id, limit=limit, offset=offset)

    async def list_production_environments(
        self, principal: Principal, production_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        async with self._uow_factory(principal) as uow:
            production = await uow.productions.get_by_id(production_id)
            if production is None:
                raise NotFound("Production does not exist.")
            await require_project_role(uow, principal, production.project_id, READ_ROLES)
            return await uow.environments.list_by_production(
                production_id, limit=limit, offset=offset
            )

    async def list_environment_types(self, principal: Principal) -> list[EnvironmentType]:
        async with self._uow_factory(principal) as uow:
            return await uow.environment_types.list_enabled()

    async def get_supported_tabs(
        self, principal: Principal, environment_id: UUID
    ) -> tuple[str, ...]:
        async with self._uow_factory(principal) as uow:
            environment = await self._require_environment(uow, environment_id)
            await require_project_role(uow, principal, environment.project_id, READ_ROLES)
            environment_type = await self._require_type(uow, environment.environment_type_id)
            return EnvironmentCompatibilityService.resolve_supported_environment_tabs(
                environment_type
            )

    async def get_readiness(
        self, principal: Principal, environment_id: UUID
    ) -> EnvironmentReadiness:
        return (await self.get_environment(principal, environment_id)).readiness

    async def get_compatible_assets(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
        subcategory: str | None = None,
    ) -> list[EnvironmentAssetManifest]:
        async with self._uow_factory(principal) as uow:
            environment = await self._require_environment(uow, environment_id)
            await require_project_role(uow, principal, environment.project_id, READ_ROLES)
            environment_type = await self._require_type(uow, environment.environment_type_id)
            return await EnvironmentCompatibilityService(
                uow.environment_assets
            ).get_compatible_assets(
                environment=environment,
                environment_type=environment_type,
                category=category,
                limit=limit,
                offset=offset,
                subcategory=subcategory,
            )

    async def update_identity(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> EnvironmentMutationResult:
        values = {"display_name": display_name, "description": description}

        async def transform(
            _uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            return current.update_properties(display_name=display_name, description=description), {
                key: value for key, value in values.items() if value is not None
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.identity_updated",
            event_type="environment.identity_updated",
            request_payload=values,
            transform=transform,
        )

    async def update_properties(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
        display_name: str | None = None,
        description: str | None = None,
        location_type: EnvironmentLocationType | None = None,
        interior_exterior: InteriorExterior | None = None,
        biome: str | None = None,
        climate_profile: str | None = None,
        time_of_day: str | None = None,
        scale: int | None = None,
        navigation_constraints: str | None = None,
        camera_access_constraints: str | None = None,
        weather_profile_id: UUID | None = None,
        atmosphere_profile_id: UUID | None = None,
        style_profile_id: UUID | None = None,
        lighting_compatibility_profile_id: UUID | None = None,
        camera_compatibility_profile_id: UUID | None = None,
        audio_compatibility_profile_id: UUID | None = None,
        vfx_compatibility_profile_id: UUID | None = None,
    ) -> EnvironmentMutationResult:
        values = {
            "display_name": display_name,
            "description": description,
            "location_type": location_type,
            "interior_exterior": interior_exterior,
            "biome": biome,
            "climate_profile": climate_profile,
            "time_of_day": time_of_day,
            "scale": scale,
            "navigation_constraints": navigation_constraints,
            "camera_access_constraints": camera_access_constraints,
            "weather_profile_id": weather_profile_id,
            "atmosphere_profile_id": atmosphere_profile_id,
            "style_profile_id": style_profile_id,
            "lighting_compatibility_profile_id": lighting_compatibility_profile_id,
            "camera_compatibility_profile_id": camera_compatibility_profile_id,
            "audio_compatibility_profile_id": audio_compatibility_profile_id,
            "vfx_compatibility_profile_id": vfx_compatibility_profile_id,
        }

        async def transform(
            _uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            return current.update_properties(
                display_name=display_name,
                description=description,
                location_type=location_type,
                interior_exterior=interior_exterior,
                biome=biome,
                climate_profile=climate_profile,
                time_of_day=time_of_day,
                scale=scale,
                navigation_constraints=navigation_constraints,
                camera_access_constraints=camera_access_constraints,
                weather_profile_id=weather_profile_id,
                atmosphere_profile_id=atmosphere_profile_id,
                style_profile_id=style_profile_id,
                lighting_compatibility_profile_id=lighting_compatibility_profile_id,
                camera_compatibility_profile_id=camera_compatibility_profile_id,
                audio_compatibility_profile_id=audio_compatibility_profile_id,
                vfx_compatibility_profile_id=vfx_compatibility_profile_id,
            ), {key: value for key, value in values.items() if value is not None}

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.properties_updated",
            event_type="environment.properties_updated",
            request_payload=values,
            transform=transform,
        )

    async def change_type(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        environment_type_id: UUID,
        expected_version: int,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        async def transform(
            uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            environment_type = await self._require_type(uow, environment_type_id)
            resolution = await EnvironmentCompatibilityService(
                uow.environment_assets
            ).resolve_type_change(environment=current, environment_type=environment_type)
            updated = current.change_type(
                environment_type.environment_type_id,
                cleared_scalar_fields=frozenset(resolution.cleared_fields),
                preserved_collections=resolution.preserved_collections,
            )
            return updated, {
                "previous_environment_type_id": str(current.environment_type_id),
                "environment_type_id": str(environment_type_id),
                "preserved_asset_ids": [str(item) for item in resolution.preserved_asset_ids],
                "cleared_asset_ids": [str(item) for item in resolution.cleared_asset_ids],
                "cleared_fields": list(resolution.cleared_fields),
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.type_changed",
            event_type="environment.type_changed",
            request_payload={"environment_type_id": str(environment_type_id)},
            transform=transform,
        )

    async def select_asset(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        category: str,
        asset_id: UUID,
        expected_version: int,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        async def transform(
            uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            environment_type = await self._require_type(uow, current.environment_type_id)
            manifest = await EnvironmentCompatibilityService(
                uow.environment_assets
            ).validate_selection(
                environment=current,
                environment_type=environment_type,
                asset_id=asset_id,
            )
            if manifest.category != category:
                raise InvariantViolation(
                    f"Environment asset {asset_id} is not in the {category} category."
                )
            return current.select_asset(category, asset_id), {
                "category": category,
                "asset_id": str(asset_id),
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.asset_selected",
            event_type="environment.asset_selected",
            request_payload={"category": category, "asset_id": str(asset_id)},
            transform=transform,
        )

    async def replace_assets(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        category: str,
        asset_ids: tuple[UUID, ...],
        expected_version: int,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        if category not in ENVIRONMENT_COLLECTION_SELECTIONS:
            raise InvariantViolation("Environment category is not multi-select.")

        async def transform(
            uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            environment_type = await self._require_type(uow, current.environment_type_id)
            compatibility = EnvironmentCompatibilityService(uow.environment_assets)
            candidate = current.replace_assets(category, asset_ids)
            for asset_id in asset_ids:
                manifest = await uow.environment_assets.get_by_id(asset_id)
                if manifest is None:
                    raise NotFound("Environment asset does not exist.")
                if manifest.category != category:
                    raise InvariantViolation(
                        f"Environment asset {asset_id} is not in the {category} category."
                    )
                reasons = compatibility.validate_manifest(
                    environment=candidate,
                    environment_type=environment_type,
                    manifest=manifest,
                    selected_ids=frozenset(candidate.selected_asset_ids),
                )
                if reasons:
                    raise InvariantViolation("; ".join(reasons))
            return candidate, {
                "category": category,
                "asset_ids": [str(item) for item in asset_ids],
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.assets_replaced",
            event_type="environment.assets_replaced",
            request_payload={
                "category": category,
                "asset_ids": [str(item) for item in asset_ids],
            },
            transform=transform,
        )

    async def remove_asset(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        category: str,
        asset_id: UUID | None,
        expected_version: int,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        async def transform(
            _uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            return current.remove_asset(category, asset_id), {
                "category": category,
                "asset_id": str(asset_id) if asset_id else None,
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.asset_removed",
            event_type="environment.asset_removed",
            request_payload={
                "category": category,
                "asset_id": str(asset_id) if asset_id else None,
            },
            transform=transform,
        )

    async def validate_package(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        async def transform(
            uow: UnitOfWork, current: Environment
        ) -> tuple[Environment, dict[str, Any]]:
            environment_type = await self._require_type(uow, current.environment_type_id)
            assessment = await EnvironmentCompatibilityService(
                uow.environment_assets
            ).validate_environment_package(environment=current, environment_type=environment_type)
            updated = current.validate_readiness(
                assessment.blocking_issues,
                warnings=assessment.warnings,
                missing_requirements=assessment.missing_requirements,
                invalid_asset_ids=assessment.invalid_asset_ids,
                required_processing_jobs=assessment.required_processing_jobs,
            )
            return updated, {
                "readiness_status": updated.readiness_status,
                "blocking_issues": list(assessment.blocking_issues),
                "warnings": list(assessment.warnings),
                "missing_requirements": list(assessment.missing_requirements),
                "invalid_asset_ids": [str(item) for item in assessment.invalid_asset_ids],
                "required_processing_jobs": list(assessment.required_processing_jobs),
            }

        return await self._mutate(
            principal,
            environment_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="environment.readiness_changed",
            event_type="environment.readiness_changed",
            request_payload={},
            transform=transform,
        )

    async def _mutate(
        self,
        principal: Principal,
        environment_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
        action: str,
        event_type: str,
        request_payload: dict[str, Any],
        transform: EnvironmentTransform,
    ) -> EnvironmentMutationResult:
        request_hash = self._hash(
            {
                "operation": action,
                "environment_id": str(environment_id),
                "expected_version": expected_version,
                **request_payload,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            environment = await self.get_environment(principal, environment_id)
            return EnvironmentMutationResult(
                environment,
                claim.response.get("change_summary", {}),
                claim.response,
            )
        try:
            async with self._uow_factory(principal) as uow:
                current = await self._require_environment(uow, environment_id)
                await require_project_role(uow, principal, current.project_id, EDIT_ROLES)
                self._require_version(current, expected_version)
                updated, summary = await transform(uow, current)
                response = self._mutation_response(updated, summary)
                if updated.version == current.version:
                    await uow.idempotency.complete(idempotency_key, response)
                    await uow.commit()
                    return EnvironmentMutationResult(updated, {**summary, "no_op": True})
                await uow.environments.update(updated, expected_version=expected_version)
                await uow.outbox.append(
                    event_type,
                    1,
                    self._event_payload(updated, previous_version=current.version, summary=summary),
                    aggregate_id=updated.environment_id,
                    aggregate_sequence=updated.version,
                )
                await uow.idempotency.complete(idempotency_key, response)
                await self._queue_audit_success(
                    uow,
                    principal,
                    updated,
                    idempotency_key=idempotency_key,
                    action=action,
                    previous_version=current.version,
                    summary=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action=action)
            return EnvironmentMutationResult(updated, summary)
        except Exception as exc:
            await self._mutation_failure(principal, idempotency_key, action, environment_id, exc)
            raise

    @staticmethod
    async def _require_environment(uow: UnitOfWork, environment_id: UUID) -> Environment:
        environment = await uow.environments.get_by_id(environment_id)
        if environment is None:
            raise NotFound("Environment does not exist.")
        return environment

    @staticmethod
    async def _require_type(uow: UnitOfWork, environment_type_id: UUID) -> EnvironmentType:
        environment_type = await uow.environment_types.get_by_id(environment_type_id)
        if environment_type is None or not environment_type.enabled:
            raise NotFound("Environment type does not exist or is disabled.")
        return environment_type

    @staticmethod
    def _require_version(environment: Environment, expected_version: int) -> None:
        if environment.version != expected_version:
            raise ConcurrencyConflict(
                f"Expected environment version {expected_version}, found {environment.version}."
            )

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @staticmethod
    def _event_payload(
        environment: Environment, *, previous_version: int, summary: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "environment_id": str(environment.environment_id),
            "workspace_id": str(environment.workspace_id),
            "project_id": str(environment.project_id),
            "production_id": str(environment.production_id),
            "previous_version": previous_version,
            "version": environment.version,
            "change_summary": summary,
        }

    @staticmethod
    def _mutation_response(environment: Environment, summary: dict[str, Any]) -> dict[str, Any]:
        from app.interfaces.http.environment_schemas import EnvironmentResponse

        return {
            "environment": EnvironmentResponse.from_domain(environment).model_dump(mode="json"),
            "change_summary": summary,
        }

    @staticmethod
    def _audit_key(action: str, idempotency_key: str, outcome: str) -> str:
        return f"{action}:{idempotency_key}:{outcome}"

    async def _queue_audit_success(
        self,
        uow: UnitOfWork,
        principal: Principal,
        environment: Environment,
        *,
        idempotency_key: str,
        action: str,
        previous_version: int,
        summary: dict[str, Any],
    ) -> None:
        await uow.audit_queue.enqueue(
            deduplication_key=self._audit_key(action, idempotency_key, "success"),
            principal=principal,
            action=action,
            outcome="success",
            resource_id=environment.environment_id,
            details={
                "tenant_id": str(environment.workspace_id),
                "project_id": str(environment.project_id),
                "production_id": str(environment.production_id),
                "environment_id": str(environment.environment_id),
                "previous_version": previous_version,
                "new_version": environment.version,
                "change_summary": summary,
            },
        )

    async def _deliver_audit(
        self, principal: Principal, idempotency_key: str, *, action: str
    ) -> None:
        try:
            await self._audit.deliver(
                principal.workspace_id,
                self._audit_key(action, idempotency_key, "success"),
            )
        except Exception:
            return

    async def _mutation_failure(
        self,
        principal: Principal,
        idempotency_key: str,
        action: str,
        resource_id: UUID | None,
        exc: Exception,
    ) -> None:
        error_code = getattr(exc, "code", "internal_error")
        try:
            await self._idempotency.fail(principal.workspace_id, idempotency_key, error_code)
        except Exception:
            # Failure bookkeeping must never replace the domain exception that
            # caused the command to fail (for example an RLS-hidden 404).
            pass
        try:
            await self._audit.record_or_queue(
                deduplication_key=self._audit_key(action, idempotency_key, "failure"),
                principal=principal,
                action=action,
                outcome="failure",
                resource_id=resource_id,
                details={"error": error_code},
            )
        except Exception:
            # The original command error remains the client contract. Audit
            # delivery can be reconciled independently when its tenant context
            # or database role is unavailable.
            pass
