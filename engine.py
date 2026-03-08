from __future__ import annotations

from datetime import datetime, timezone, date, timedelta

import aiosqlite

SQL_TABLES = """
CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id TEXT NOT NULL,
    author TEXT NOT NULL,
    did TEXT NOT NULL,
    next TEXT NOT NULL,
    blockers TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS team_members (
    team_id TEXT NOT NULL,
    member TEXT NOT NULL,
    PRIMARY KEY (team_id, member)
);
"""


async def init_db(path: str) -> aiosqlite.Connection:
    db = await aiosqlite.connect(path)
    db.row_factory = aiosqlite.Row
    await db.executescript(SQL_TABLES)
    await db.commit()
    return db


def _row(r: aiosqlite.Row) -> dict:
    return {k: r[k] for k in r.keys()}


async def post_update(db: aiosqlite.Connection, data: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    cur = await db.execute(
        "INSERT INTO updates (team_id, author, did, next, blockers, created_at) VALUES (?,?,?,?,?,?)",
        (data["team_id"], data["author"], data["did"], data["next"], data.get("blockers"), now),
    )
    await db.commit()
    rows = await db.execute_fetchall("SELECT * FROM updates WHERE id = ?", (cur.lastrowid,))
    return _row(rows[0])


async def list_updates(db: aiosqlite.Connection, team_id: str, for_date: str | None = None) -> list[dict]:
    if for_date:
        rows = await db.execute_fetchall(
            "SELECT * FROM updates WHERE team_id = ? AND DATE(created_at) = ? ORDER BY created_at DESC",
            (team_id, for_date),
        )
    else:
        rows = await db.execute_fetchall(
            "SELECT * FROM updates WHERE team_id = ? ORDER BY created_at DESC LIMIT 100",
            (team_id,),
        )
    return [_row(r) for r in rows]


async def get_digest(db: aiosqlite.Connection, team_id: str, for_date: str | None = None) -> dict:
    target = for_date or date.today().isoformat()
    updates = await list_updates(db, team_id, target)
    blockers = [u["blockers"] for u in updates if u["blockers"]]
    authors_done = {u["author"] for u in updates}

    members_rows = await db.execute_fetchall(
        "SELECT member FROM team_members WHERE team_id = ?", (team_id,)
    )
    all_members = {r["member"] for r in members_rows}
    missing = sorted(all_members - authors_done)

    return {
        "team_id": team_id,
        "date": target,
        "updates": updates,
        "blockers_summary": blockers,
        "authors_missing": missing,
        "total_updates": len(updates),
    }


async def set_team_members(db: aiosqlite.Connection, team_id: str, members: list[str]) -> None:
    await db.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
    for m in members:
        await db.execute(
            "INSERT OR IGNORE INTO team_members (team_id, member) VALUES (?,?)", (team_id, m)
        )
    await db.commit()


async def get_team_members(db: aiosqlite.Connection, team_id: str) -> list[str]:
    rows = await db.execute_fetchall(
        "SELECT member FROM team_members WHERE team_id = ? ORDER BY member", (team_id,)
    )
    return [r["member"] for r in rows]


async def get_streak(db: aiosqlite.Connection, team_id: str) -> dict:
    """Calculate how many consecutive days the team has posted at least one update."""
    rows = await db.execute_fetchall(
        "SELECT DISTINCT DATE(created_at) as d FROM updates WHERE team_id = ? ORDER BY d DESC",
        (team_id,),
    )
    dates = [r["d"] for r in rows]
    if not dates:
        return {"team_id": team_id, "streak_days": 0, "last_active": None}

    streak = 1
    today = date.today()
    last = date.fromisoformat(dates[0])

    # Allow today or yesterday as the start of streak
    if (today - last).days > 1:
        return {"team_id": team_id, "streak_days": 0, "last_active": dates[0]}

    for i in range(1, len(dates)):
        prev = date.fromisoformat(dates[i])
        if (last - prev).days == 1:
            streak += 1
            last = prev
        else:
            break

    return {"team_id": team_id, "streak_days": streak, "last_active": dates[0]}
