import json
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.types import Activity, Context, Identity


class SqlSemanticProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_identity(self, identity: Identity) -> None:
        await self._session.execute(
            text(
                """
                insert into identities (
                    id, workspace_id, kind, canonical_key, revision, created_at
                ) values (
                    :id, :workspace_id, :kind, :canonical_key, :revision, :created_at
                )
                """
            ),
            {
                "id": identity.id,
                "workspace_id": identity.workspace_id,
                "kind": identity.kind.value,
                "canonical_key": identity.canonical_key,
                "revision": identity.revision,
                "created_at": identity.created_at,
            },
        )

    async def add_context(self, context: Context) -> None:
        await self._session.execute(
            text(
                """
                insert into contexts (
                    identity_id, workspace_id, kind, parent_context_id
                ) values (
                    :identity_id, :workspace_id, :kind, :parent_context_id
                )
                """
            ),
            {
                "identity_id": context.identity_id,
                "workspace_id": context.workspace_id,
                "kind": context.kind.value,
                "parent_context_id": context.parent_context_id,
            },
        )

    async def add_activity(self, activity: Activity) -> None:
        await self._session.execute(
            text(
                """
                insert into activities (
                    id, workspace_id, activity_type, performed_by, context_id,
                    started_at, ended_at, attributes
                ) values (
                    :id, :workspace_id, :activity_type, :performed_by, :context_id,
                    :started_at, :ended_at, cast(:attributes as jsonb)
                )
                """
            ),
            {
                "id": activity.id,
                "workspace_id": activity.workspace_id,
                "activity_type": activity.activity_type,
                "performed_by": activity.performed_by,
                "context_id": activity.context_id,
                "started_at": activity.started_at,
                "ended_at": activity.ended_at,
                "attributes": json.dumps(activity.attributes),
            },
        )

    async def add_activity_output(
        self,
        *,
        workspace_id: UUID,
        activity_id: UUID,
        identity_id: UUID,
    ) -> None:
        await self._session.execute(
            text(
                """
                insert into activity_participations (
                    workspace_id, activity_id, identity_id, role
                ) values (:workspace_id, :activity_id, :identity_id, 'output')
                """
            ),
            {
                "workspace_id": workspace_id,
                "activity_id": activity_id,
                "identity_id": identity_id,
            },
        )
