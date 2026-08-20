from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.errors import AuthorizationDenied, ConcurrencyConflict, InvariantViolation


class ProjectRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectLifecycle(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProductionState(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


_PRODUCTION_TRANSITIONS: dict[ProductionState, frozenset[ProductionState]] = {
    ProductionState.PLANNED: frozenset(
        {ProductionState.ACTIVE, ProductionState.ARCHIVED}
    ),
    ProductionState.ACTIVE: frozenset(
        {
            ProductionState.PAUSED,
            ProductionState.COMPLETED,
            ProductionState.ARCHIVED,
        }
    ),
    ProductionState.PAUSED: frozenset(
        {ProductionState.ACTIVE, ProductionState.ARCHIVED}
    ),
    ProductionState.COMPLETED: frozenset(
        {ProductionState.ACTIVE, ProductionState.ARCHIVED}
    ),
    ProductionState.ARCHIVED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID
    workspace_id: UUID
    identity_id: UUID
    context_id: UUID
    owner_principal_id: UUID
    created_by_principal_id: UUID
    name: str
    lifecycle: ProjectLifecycle
    version: int
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        project_id: UUID,
        workspace_id: UUID,
        context_id: UUID,
        owner_principal_id: UUID,
        name: str,
        now: datetime,
    ) -> "Project":
        normalized_name = name.strip()
        if not normalized_name:
            raise InvariantViolation("Project name is required.")
        return cls(
            id=project_id,
            workspace_id=workspace_id,
            identity_id=project_id,
            context_id=context_id,
            owner_principal_id=owner_principal_id,
            created_by_principal_id=owner_principal_id,
            name=normalized_name,
            lifecycle=ProjectLifecycle.ACTIVE,
            version=1,
            created_at=now,
            updated_at=now,
        )

    def transfer_ownership(
        self,
        *,
        current_principal_id: UUID,
        target_principal_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> "Project":
        self._require_version(expected_version)
        if self.lifecycle is ProjectLifecycle.ARCHIVED:
            raise InvariantViolation("Archived Projects are read-only.")
        if current_principal_id != self.owner_principal_id:
            raise AuthorizationDenied("Only the current Project Owner may transfer ownership.")
        if target_principal_id == self.owner_principal_id:
            raise InvariantViolation("The target principal is already the Project Owner.")
        return replace(
            self,
            owner_principal_id=target_principal_id,
            version=self.version + 1,
            updated_at=now,
        )

    def archive(self, *, expected_version: int, now: datetime) -> "Project":
        self._require_version(expected_version)
        if self.lifecycle is ProjectLifecycle.ARCHIVED:
            raise InvariantViolation("Project is already archived.")
        return replace(
            self,
            lifecycle=ProjectLifecycle.ARCHIVED,
            archived_at=now,
            version=self.version + 1,
            updated_at=now,
        )

    def restore(
        self,
        *,
        principal_id: UUID,
        expected_version: int,
        now: datetime,
    ) -> "Project":
        self._require_version(expected_version)
        if principal_id != self.owner_principal_id:
            raise AuthorizationDenied("Only the Project Owner may restore an archived Project.")
        if self.lifecycle is not ProjectLifecycle.ARCHIVED:
            raise InvariantViolation("Only an archived Project may be restored.")
        return replace(
            self,
            lifecycle=ProjectLifecycle.ACTIVE,
            archived_at=None,
            version=self.version + 1,
            updated_at=now,
        )

    def _require_version(self, expected_version: int) -> None:
        if expected_version != self.version:
            raise ConcurrencyConflict(
                f"Expected Project version {expected_version}; current version is {self.version}."
            )


@dataclass(frozen=True, slots=True)
class ProjectMembership:
    id: UUID
    workspace_id: UUID
    project_id: UUID
    principal_id: UUID
    role: ProjectRole
    valid_from: datetime
    valid_to: datetime | None
    granted_by_agent_id: UUID


@dataclass(frozen=True, slots=True)
class Production:
    id: UUID
    workspace_id: UUID
    project_id: UUID
    name: str
    state: ProductionState
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        production_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        name: str,
        now: datetime,
    ) -> "Production":
        normalized_name = name.strip()
        if not normalized_name:
            raise InvariantViolation("Production name is required.")
        return cls(
            id=production_id,
            workspace_id=workspace_id,
            project_id=project_id,
            name=normalized_name,
            state=ProductionState.PLANNED,
            version=1,
            created_at=now,
            updated_at=now,
        )

    def transition(
        self,
        *,
        target: ProductionState,
        expected_version: int,
        project_lifecycle: ProjectLifecycle,
        now: datetime,
    ) -> "Production":
        if expected_version != self.version:
            raise ConcurrencyConflict(
                f"Expected Production version {expected_version}; "
                f"current version is {self.version}."
            )
        if project_lifecycle is ProjectLifecycle.ARCHIVED:
            raise InvariantViolation("Productions in archived Projects are read-only.")
        if target not in _PRODUCTION_TRANSITIONS[self.state]:
            raise InvariantViolation(
                f"Production transition {self.state.value} -> {target.value} is not allowed."
            )
        return replace(self, state=target, version=self.version + 1, updated_at=now)


def require_project_mutation_role(role: ProjectRole) -> None:
    if role not in {ProjectRole.OWNER, ProjectRole.ADMIN, ProjectRole.EDITOR}:
        raise AuthorizationDenied("Project Editor, Admin, or Owner authority is required.")
