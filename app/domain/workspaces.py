from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.errors import AuthorizationDenied, InvariantViolation


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass(frozen=True, slots=True)
class WorkspaceMembership:
    workspace_id: UUID
    principal_id: UUID
    agent_id: UUID
    role: WorkspaceRole
    valid_from: datetime
    valid_to: datetime | None

    def is_active(self, at: datetime) -> bool:
        return self.valid_from <= at and (self.valid_to is None or at < self.valid_to)


def require_project_create_authority(role: WorkspaceRole) -> None:
    if role not in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}:
        raise AuthorizationDenied("Workspace Owner or Admin authority is required.")


def require_project_role_compatible(
    workspace_role: WorkspaceRole,
    project_role: str,
) -> None:
    if workspace_role is WorkspaceRole.VIEWER and project_role != "viewer":
        raise InvariantViolation("A Workspace Viewer may only receive Project Viewer access.")
