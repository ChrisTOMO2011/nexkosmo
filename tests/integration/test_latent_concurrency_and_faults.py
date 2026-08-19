import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_concurrent_idempotency_claim_allows_one_logical_owner(db):
    engine = db.engine
    workspace_id = uuid4()
    key = f"latent-{uuid4()}"
    async with engine.begin() as setup:
        await setup.execute(
            text("insert into workspaces (id, canonical_key) values (:id, :key)"),
            {"id": workspace_id, "key": f"latent-workspace-{workspace_id}"},
        )

    barrier = asyncio.Event()
    ready = 0
    ready_lock = asyncio.Lock()

    async def claimant() -> bool:
        nonlocal ready
        async with engine.connect() as conn:
            tx = await conn.begin()
            try:
                async with ready_lock:
                    ready += 1
                    if ready == 2:
                        barrier.set()
                await barrier.wait()
                result = await conn.execute(
                    text(
                        """
                        insert into idempotency_records (
                            workspace_id, idempotency_key, request_hash, status,
                            owner_token, lease_expires_at
                        ) values (
                            :workspace_id, :key, 'same-request', 'processing',
                            gen_random_uuid(), now() + interval '5 minutes'
                        )
                        on conflict (workspace_id, idempotency_key) do nothing
                        """
                    ),
                    {"workspace_id": workspace_id, "key": key},
                )
                await tx.commit()
                return result.rowcount == 1
            except Exception:
                await tx.rollback()
                raise

    claimed = await asyncio.gather(claimant(), claimant())
    assert sum(claimed) == 1

    async with engine.connect() as verify:
        count = await verify.scalar(
            text(
                "select count(*) from idempotency_records "
                "where workspace_id=:workspace_id and idempotency_key=:key"
            ),
            {"workspace_id": workspace_id, "key": key},
        )
    assert count == 1


@pytest.mark.asyncio
async def test_transaction_fault_rolls_back_partial_state(db):
    engine = db.engine
    workspace_id = uuid4()
    canonical_key = f"fault-workspace-{workspace_id}"
    tx = None

    try:
        async with engine.connect() as conn:
            tx = await conn.begin()
            await conn.execute(
                text("insert into workspaces (id, canonical_key) values (:id, :key)"),
                {"id": workspace_id, "key": canonical_key},
            )
            raise RuntimeError("simulated mid-transaction failure")
    except RuntimeError:
        if tx is not None and tx.is_active:
            await tx.rollback()

    async with engine.connect() as verify:
        count = await verify.scalar(
            text("select count(*) from workspaces where id=:id"),
            {"id": workspace_id},
        )
    assert count == 0


@pytest.mark.asyncio
async def test_duplicate_primary_claim_without_conflict_handling_is_detected(db):
    workspace_id = uuid4()
    key = f"duplicate-{uuid4()}"
    await db.execute(
        text("insert into workspaces (id, canonical_key) values (:id, :key)"),
        {"id": workspace_id, "key": f"dup-workspace-{workspace_id}"},
    )
    await db.execute(
        text(
            """
            insert into idempotency_records (
                workspace_id, idempotency_key, request_hash, status,
                owner_token, lease_expires_at
            ) values (
                :workspace_id, :key, 'same-request', 'processing',
                gen_random_uuid(), now() + interval '5 minutes'
            )
            """
        ),
        {"workspace_id": workspace_id, "key": key},
    )

    with pytest.raises(IntegrityError):
        async with db.begin_nested():
            await db.execute(
                text(
                    """
                    insert into idempotency_records (
                        workspace_id, idempotency_key, request_hash, status,
                        owner_token, lease_expires_at
                    ) values (
                        :workspace_id, :key, 'same-request', 'processing',
                        gen_random_uuid(), now() + interval '5 minutes'
                    )
                    """
                ),
                {"workspace_id": workspace_id, "key": key},
            )
