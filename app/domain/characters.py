from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from app.domain.errors import ConcurrencyConflict, InvariantViolation


@dataclass(frozen=True, slots=True)
class Character:
    id: UUID
    workspace_id: UUID
    project_id: UUID
    identity_id: UUID
    created_by_principal_id: UUID
    display_name: str
    role_label: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        character_id: UUID,
        workspace_id: UUID,
        project_id: UUID,
        created_by_principal_id: UUID,
        display_name: str,
        role_label: str | None,
        now: datetime,
    ) -> "Character":
        return cls(
            id=character_id,
            workspace_id=workspace_id,
            project_id=project_id,
            identity_id=character_id,
            created_by_principal_id=created_by_principal_id,
            display_name=_normalize_display_name(display_name),
            role_label=_normalize_role_label(role_label),
            version=1,
            created_at=now,
            updated_at=now,
        )

    def update_metadata(
        self,
        *,
        expected_version: int,
        now: datetime,
        display_name: str | None = None,
        role_label: str | None = None,
        replace_role_label: bool = False,
    ) -> "Character":
        self._require_version(expected_version)
        next_display_name = (
            self.display_name
            if display_name is None
            else _normalize_display_name(display_name)
        )
        next_role_label = (
            _normalize_role_label(role_label) if replace_role_label else self.role_label
        )
        if (
            next_display_name == self.display_name
            and next_role_label == self.role_label
        ):
            raise InvariantViolation("Character metadata update must change a value.")
        return replace(
            self,
            display_name=next_display_name,
            role_label=next_role_label,
            version=self.version + 1,
            updated_at=now,
        )

    def _require_version(self, expected_version: int) -> None:
        if expected_version != self.version:
            raise ConcurrencyConflict(
                f"Expected Character version {expected_version}; "
                f"current version is {self.version}."
            )


def _normalize_display_name(value: str) -> str:
    normalized = value.strip()
    if not 1 <= len(normalized) <= 160:
        raise InvariantViolation("Character display name must be 1-160 characters.")
    return normalized


def _normalize_role_label(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > 160:
        raise InvariantViolation("Character role label must be at most 160 characters.")
    return normalized
