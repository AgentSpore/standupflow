from __future__ import annotations
from pydantic import BaseModel


class UpdateCreate(BaseModel):
    team_id: str
    author: str
    did: str           # What I did
    next: str          # What I'm doing next
    blockers: str | None = None


class UpdateResponse(BaseModel):
    id: int
    team_id: str
    author: str
    did: str
    next: str
    blockers: str | None
    created_at: str


class DigestResponse(BaseModel):
    team_id: str
    date: str
    updates: list[UpdateResponse]
    blockers_summary: list[str]
    authors_missing: list[str]
    total_updates: int
