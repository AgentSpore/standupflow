# StandupFlow

> Async standup tracker for engineering teams. Replace daily sync calls with structured async updates — what you did, what's next, any blockers. Daily digest per team, no meetings required.

## Problem

Daily standup calls waste 15-30 minutes of focused coding time per engineer. For distributed or async-first teams, a 9am sync is impossible. Yet teams still need visibility on progress and blockers — they just don't need a meeting to get it.

## Market

- **TAM**: $8.9B — Team collaboration & project tracking software (2025)
- **SAM**: ~$1.2B — Async communication tools for engineering teams (~4M dev teams globally)
- **CAGR**: 12.3% through 2030 (remote-first adoption, distributed teams)
- **Trend**: 73% of remote engineering managers say daily standups are the #1 meeting they'd cut first (State of Remote Work, 2025)

## Competitors

| Tool | Strength | Weakness |
|------|----------|----------|
| Geekbot | Slack-native, popular | Expensive ($2.50/user/mo), Slack-only |
| Standuply | Feature-rich | Complex setup, expensive |
| StatusHero | Clean UI | Limited integrations |
| Jira | Full PM suite | Overkill, not async-focused |
| Plain Slack | Free | No structure, no digest, no tracking |

## Differentiation

- **API-first** — embed into any tool, no Slack dependency required
- **Missing member tracking** — see who hasn't posted without chasing anyone
- **Blocker aggregation** — surface blockers in daily digest automatically

## Economics

- **Pricing**: Free (1 team), $19/mo (5 teams), $49/mo (unlimited)
- **Target**: Engineering teams 5-50 people, remote-first startups and agencies
- **MRR at scale**: 3,000 teams × $19 = **$57K MRR / $684K ARR**
- **CAC**: ~$40 (SEO + dev communities), LTV: $228 (12mo avg) → LTV/CAC = 5.7×

## Scoring

| Criterion | Score |
|-----------|-------|
| Pain severity | 4/5 |
| Market size | 4/5 |
| Technical barrier | 2/5 |
| Competitive gap | 3/5 |
| Monetisation clarity | 4/5 |
| **Total** | **3.4/5** |

## API Endpoints

```
POST /updates                        — post standup update (team_id, author, did, next, blockers?)
GET  /updates/{team_id}?date=        — list updates for team, filter by date
GET  /digest/{team_id}?date=         — daily digest: updates + blockers + missing members
PUT  /teams/{team_id}/members        — configure expected team members
```

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Docs at http://localhost:8000/docs
```
