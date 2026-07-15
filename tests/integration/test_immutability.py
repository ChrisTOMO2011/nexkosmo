from sqlalchemy import text
from sqlalchemy.exc import DBAPIError


async def test_assertion_update_is_rejected_by_database(db):
    row = await db.scalar(text("SELECT id FROM assertions LIMIT 1"))
    if row is None:
        return
    try:
        await db.execute(
            text("UPDATE assertions SET predicate_key='corrupted' WHERE id=:id"),
            {"id": row},
        )
    except DBAPIError:
        return
    raise AssertionError("Permanent assertion update unexpectedly succeeded.")
