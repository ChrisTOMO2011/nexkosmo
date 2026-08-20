from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Literal, Self, cast
from uuid import UUID, uuid4

from app.domain.errors import InvariantViolation

ProjectStatus = Literal["active", "archived"]
ProjectMemberRole = Literal["Owner", "Admin", "Editor", "Viewer"]
ProductionType = Literal[
    "Feature Film",
    "Short Film",
    "TV",
    "Commercial",
    "Music Video",
    "Social",
    "Animation",
    "Documentary",
    "Custom",
]
ProductionStatus = Literal[
    "draft",
    "pre-production",
    "production",
    "post-production",
    "completed",
    "archived",
]

PROJECT_STATUSES = frozenset({"active", "archived"})
PROJECT_MEMBER_ROLES = frozenset({"Owner", "Admin", "Editor", "Viewer"})
PRODUCTION_TYPES = frozenset(
    {
        "Feature Film",
        "Short Film",
        "TV",
        "Commercial",
        "Music Video",
        "Social",
        "Animation",
        "Documentary",
        "Custom",
    }
)
PRODUCTION_STATUSES = frozenset(
    {
        "draft",
        "pre-production",
        "production",
        "post-production",
        "completed",
        "archived",
    }
)


@dataclass(frozen=True, slots=True)
class Project:
    project_id: UUID
    workspace_id: UUID
    name: str
    description: str
    status: ProjectStatus
    owner_id: UUID
    member_ids: tuple[UUID, ...]
    created_at: datetime
    updated_at: datetime
    version: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolation("Project name is required.")
        if self.name != self.name.strip():
            raise InvariantViolation("Project name must be trimmed.")
        if self.description != self.description.strip():
            raise InvariantViolation("Project description must be trimmed.")
        if self.status not in PROJECT_STATUSES:
            raise InvariantViolation("Project status is not supported.")
        if self.owner_id not in self.member_ids:
            raise InvariantViolation("Project owner must be a project member.")
        if len(self.member_ids) != len(set(self.member_ids)):
            raise InvariantViolation("Project members must be unique.")
        if self.version < 1:
            raise InvariantViolation("Project version must be positive.")
        if self.updated_at < self.created_at:
            raise InvariantViolation("Project updated_at cannot precede created_at.")

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        name: str,
        description: str,
        owner_id: UUID,
        project_id: UUID | None = None,
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        return cls(
            project_id=project_id or uuid4(),
            workspace_id=workspace_id,
            name=name.strip(),
            description=description.strip(),
            status="active",
            owner_id=owner_id,
            member_ids=(owner_id,),
            created_at=timestamp,
            updated_at=timestamp,
            version=1,
        )

    def _evolve(self, *, now: datetime | None = None, **changes: object) -> Self:
        return replace(
            self,
            **cast(Any, changes),
            version=self.version + 1,
            updated_at=now or datetime.now(UTC),
        )

    def rename(self, name: str, *, now: datetime | None = None) -> Self:
        value = name.strip()
        if not value:
            raise InvariantViolation("Project name is required.")
        return self._evolve(name=value, now=now)

    def archive(self, *, now: datetime | None = None) -> Self:
        return self._evolve(status="archived", now=now)

    def restore(self, *, now: datetime | None = None) -> Self:
        return self._evolve(status="active", now=now)

    def add_member(self, principal_id: UUID, *, now: datetime | None = None) -> Self:
        if principal_id in self.member_ids:
            return self
        return self._evolve(
            member_ids=(*self.member_ids, principal_id),
            now=now,
        )

    def remove_member(self, principal_id: UUID, *, now: datetime | None = None) -> Self:
        if principal_id == self.owner_id:
            raise InvariantViolation("Project owner cannot be removed.")
        if principal_id not in self.member_ids:
            return self
        return self._evolve(
            member_ids=tuple(
                member_id for member_id in self.member_ids if member_id != principal_id
            ),
            now=now,
        )

    def change_owner(self, principal_id: UUID, *, now: datetime | None = None) -> Self:
        members = (
            self.member_ids if principal_id in self.member_ids else (*self.member_ids, principal_id)
        )
        return self._evolve(owner_id=principal_id, member_ids=members, now=now)

    def update_description(self, description: str, *, now: datetime | None = None) -> Self:
        return self._evolve(description=description.strip(), now=now)

    def update(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        status: ProjectStatus | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        if name is not None:
            value = name.strip()
            if not value:
                raise InvariantViolation("Project name is required.")
            changes["name"] = value
        if description is not None:
            changes["description"] = description.strip()
        if status is not None:
            changes["status"] = status
        return self._evolve(now=now, **changes)

    def record_membership_change(self, *, now: datetime | None = None) -> Self:
        return self._evolve(now=now)


@dataclass(frozen=True, slots=True)
class Production:
    production_id: UUID
    project_id: UUID
    workspace_id: UUID
    name: str
    production_type: ProductionType
    status: ProductionStatus
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    version: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolation("Production name is required.")
        if self.name != self.name.strip():
            raise InvariantViolation("Production name must be trimmed.")
        if self.production_type not in PRODUCTION_TYPES:
            raise InvariantViolation("Production type is not supported.")
        if self.status not in PRODUCTION_STATUSES:
            raise InvariantViolation("Production status is not supported.")
        if self.version < 1:
            raise InvariantViolation("Production version must be positive.")
        if self.updated_at < self.created_at:
            raise InvariantViolation("Production updated_at cannot precede created_at.")

    @classmethod
    def create(
        cls,
        *,
        project_id: UUID,
        workspace_id: UUID,
        name: str,
        production_type: ProductionType,
        owner_id: UUID,
        production_id: UUID | None = None,
        status: ProductionStatus = "pre-production",
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        return cls(
            production_id=production_id or uuid4(),
            project_id=project_id,
            workspace_id=workspace_id,
            name=name.strip(),
            production_type=production_type,
            status=status,
            owner_id=owner_id,
            created_at=timestamp,
            updated_at=timestamp,
            version=1,
        )

    def _evolve(self, *, now: datetime | None = None, **changes: object) -> Self:
        return replace(
            self,
            **cast(Any, changes),
            version=self.version + 1,
            updated_at=now or datetime.now(UTC),
        )

    def rename(self, name: str, *, now: datetime | None = None) -> Self:
        value = name.strip()
        if not value:
            raise InvariantViolation("Production name is required.")
        return self._evolve(name=value, now=now)

    def archive(self, *, now: datetime | None = None) -> Self:
        return self._evolve(status="archived", now=now)

    def restore(self, *, now: datetime | None = None) -> Self:
        return self._evolve(status="pre-production", now=now)

    def change_status(self, status: ProductionStatus, *, now: datetime | None = None) -> Self:
        return self._evolve(status=status, now=now)

    def update(
        self,
        *,
        name: str | None = None,
        status: ProductionStatus | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        if name is not None:
            value = name.strip()
            if not value:
                raise InvariantViolation("Production name is required.")
            changes["name"] = value
        if status is not None:
            changes["status"] = status
        return self._evolve(now=now, **changes)
