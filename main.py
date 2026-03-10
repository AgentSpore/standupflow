from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import UpdateCreate, UpdateResponse, DigestResponse
from engine import (
    init_db, post_update, list_updates, get_digest,
    set_team_members, get_team_members, get_streak, get_member_stats,
    list_blockers, export_updates_csv,
)

DB_PATH = "standupflow.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await init_db(DB_PATH)
    yield
    await app.state.db.close()


app = FastAPI(
    title="StandupFlow",
    description=(
        "Async standup tracker for engineering teams. "
        "Replace daily sync calls with structured async updates. "
        "Each engineer posts: what they did, what's next, any blockers. "
        "Get a daily digest per team — no meetings required."
    ),
    version="0.4.0",
    lifespan=lifespan,
)


class TeamMembersBody(BaseModel):
    members: list[str]


@app.post("/updates", response_model=UpdateResponse, status_code=201)
async def submit_update(body: UpdateCreate):
    return await post_update(app.state.db, body.model_dump())


@app.get("/updates/{team_id}", response_model=list[UpdateResponse])
async def team_updates(
    team_id: str,
    date: str | None = Query(None, description="ISO date filter, e.g. 2026-03-08"),
):
    return await list_updates(app.state.db, team_id, date)


@app.get("/digest/{team_id}", response_model=DigestResponse)
async def daily_digest(
    team_id: str,
    date: str | None = Query(None, description="ISO date, defaults to today"),
):
    return await get_digest(app.state.db, team_id, date)


@app.put("/teams/{team_id}/members")
async def configure_team(team_id: str, body: TeamMembersBody):
    await set_team_members(app.state.db, team_id, body.members)
    return {"team_id": team_id, "members": body.members}


@app.get("/teams/{team_id}/members")
async def list_team_members(team_id: str):
    members = await get_team_members(app.state.db, team_id)
    return {"team_id": team_id, "members": members}


@app.get("/teams/{team_id}/streak")
async def team_streak(team_id: str):
    return await get_streak(app.state.db, team_id)


@app.get("/teams/{team_id}/stats")
async def member_participation_stats(team_id: str):
    return await get_member_stats(app.state.db, team_id)


@app.get("/teams/{team_id}/blockers", response_model=list[UpdateResponse])
async def team_blockers(
    team_id: str,
    since: str | None = Query(None, description="Start date ISO, e.g. 2026-03-01"),
    until: str | None = Query(None, description="End date ISO, e.g. 2026-03-31"),
    author: str | None = Query(None, description="Filter by specific team member"),
):
    """All standup updates that contain blockers. Filter by date range or author for sprint retro."""
    return await list_blockers(app.state.db, team_id, since, until, author)


@app.get("/teams/{team_id}/updates/export/csv")
async def export_updates(
    team_id: str,
    since: str | None = Query(None, description="Start date ISO"),
    until: str | None = Query(None, description="End date ISO"),
):
    """Export all team standup updates as CSV for retrospectives and sprint reporting."""
    csv_data = await export_updates_csv(app.state.db, team_id, since, until)
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=standupflow_{team_id}.csv"},
    )
