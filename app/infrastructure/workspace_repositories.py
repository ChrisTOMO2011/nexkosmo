from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.errors import AuthorizationDenied
from app.domain.workspaces import WorkspaceRole


class SqlWorkspaceAuthorityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def require_current_human_role(
        self,
        *,
        workspace_id: UUID,
        principal_id: UUID,
        agent_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> WorkspaceRole:
        if lock:
            role = await self._session.scalar(
                text(
                    """
                    select nexkosmo_private.lock_active_workspace_role(
                        :workspace_id, :principal_id, :agent_id, :at
                    )
                    """
                ),
                {
                    "workspace_id": workspace_id,
                    "principal_id": principal_id,
                    "agent_id": agent_id,
                    "at": at,
                },
            )
        else:
            role = await self._session.scalar(
                text(
                    """
                select wm.role
                from workspace_memberships wm
                join agents a
                  on a.workspace_id = wm.workspace_id
                 and a.identity_id = wm.agent_id
                where wm.workspace_id = :workspace_id
                  and wm.principal_id = :principal_id
                  and wm.agent_id = :agent_id
                  and a.kind = 'human'
                  and wm.valid_from <= :at
                  and (wm.valid_to is null or :at < wm.valid_to)
                    """
                ),
                {
                    "workspace_id": workspace_id,
                    "principal_id": principal_id,
                    "agent_id": agent_id,
                    "at": at,
                },
            )
        if role is None:
            raise AuthorizationDenied(
                "The acting agent is not an active human Workspace member for this principal."
            )
        return WorkspaceRole(role)

    async def require_active_human_principal(
        self,
        *,
        workspace_id: UUID,
        principal_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> WorkspaceRole:
        if lock:
            role = await self._session.scalar(
                text(
                    """
                    select nexkosmo_private.lock_active_human_workspace_role(
                        :workspace_id, :principal_id, :at
                    )
                    """
                ),
                {"workspace_id": workspace_id, "principal_id": principal_id, "at": at},
            )
        else:
            role = await self._session.scalar(
                text(
                    """
                select wm.role
                from workspace_memberships wm
                join agents a
                  on a.workspace_id = wm.workspace_id
                 and a.identity_id = wm.agent_id
                where wm.workspace_id = :workspace_id
                  and wm.principal_id = :principal_id
                  and a.kind = 'human'
                  and wm.valid_from <= :at
                  and (wm.valid_to is null or :at < wm.valid_to)
                    """
                ),
                {"workspace_id": workspace_id, "principal_id": principal_id, "at": at},
            )
        if role is None:
            raise AuthorizationDenied("Target is not an active human Workspace member.")
        return WorkspaceRole(role)
