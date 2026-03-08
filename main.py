from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from models import UpdateCreate, UpdateResponse, DigestResponse
from engine import (
    init_db, post_update, list_updates, get_digest,
    set_team_members, get_team_members, get_streak,
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
    version="0.2.0",
    lifespan=lifespan,
)


class TeamMembersBody(BaseModel):
    members: list[str]


@app.post("/updates", response_model=UpdateResponse, status_code=201)
async def submit_update(body: UpdateCreate):
    """Post a standup update for a team member."""
    return await post_update(app.state.db, body.model_dump())


@app.get("/updates/{team_id}", response_model=list[UpdateResponse])
async def team_updates(
    team_id: str,
    date: str | None = Query(None, description="ISO date filter, e.g. 2026-03-08"),
):
    """List standup updates for a team, optionally filtered by date."""
    return await list_updates(app.state.db, team_id, date)


@app.get("/digest/{team_id}", response_model=DigestResponse)
async def daily_digest(
    team_id: str,
    date: str | None = Query(None, description="ISO date, defaults to today"),
):
    """
    Daily digest for a team: all updates, blockers summary,
    and list of members who haven't posted yet.
    """
    return await get_digest(app.state.db, team_id, date)


@app.put("/teams/{team_id}/members")
async def configure_team(team_id: str, body: TeamMembersBody):
    """Set the expected members for a team (for missing-member tracking)."""
    await set_team_members(app.state.db, team_id, body.members)
    return {"team_id": team_id, "members": body.members}


@app.get("/teams/{team_id}/members")
async def list_team_members(team_id: str):
    """Get the configured member list for a team."""
    members = await get_team_members(app.state.db, team_id)
    return {"team_id": team_id, "members": members}


@app.get("/teams/{team_id}/streak")
async def team_streak(team_id: str):
    """
    Consecutive days the team has posted at least one standup update.
    Useful for gamification and team health tracking.
    """
    return await get_streak(app.state.db, team_id)
