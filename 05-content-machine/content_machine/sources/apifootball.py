"""API-Football v3 (api-sports.io). Docs: https://www.api-football.com/documentation-v3
Auth header `x-apisports-key`, key from https://dashboard.api-football.com.

Errors come back as HTTP 200 with a non-empty `errors` field (e.g. a free plan
asking for a season it doesn't cover), so every response is checked for that.
"""
from __future__ import annotations

import os
from datetime import date
from typing import Any, Dict, List

import httpx

from ..models import Event, FixtureSummary, Match, Team

BASE_URL = "https://v3.football.api-sports.io"
FINISHED = "FT-AET-PEN"


def make_client() -> httpx.Client:
    key = os.environ.get("API_FOOTBALL_KEY")
    if not key:
        raise RuntimeError("API_FOOTBALL_KEY missing - put it in .env (see .env.example).")
    return httpx.Client(base_url=BASE_URL, headers={"x-apisports-key": key}, timeout=20)


def _get(client: httpx.Client, path: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    resp = client.get(path, params=params)
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        raise RuntimeError(f"API-Football {path} {params}: {data['errors']}")
    return data.get("response", [])


def _season(today: date) -> int:
    # The Bundesliga starts in August; API-Football names a
    # season by its starting year.
    return today.year if today.month >= 7 else today.year - 1


def search_teams(client: httpx.Client, name: str) -> List[Dict[str, Any]]:
    return [r["team"] for r in _get(client, "/teams", {"search": name})]


def recent_finished(client: httpx.Client, team_id: int, limit: int = 5) -> List[FixtureSummary]:
    """Newest first. Not using `last=N`: the free plan rejects that parameter."""
    fixtures = _get(client, "/fixtures", {"team": team_id, "season": _season(date.today()), "status": FINISHED})
    if not fixtures:
        raise RuntimeError(f"No finished fixtures this season for team {team_id}.")
    fixtures.sort(key=lambda f: f["fixture"]["timestamp"], reverse=True)
    return [
        FixtureSummary(
            id=f["fixture"]["id"],
            date=f["fixture"]["date"][:10],
            competition=f["league"]["name"],
            home_id=f["teams"]["home"]["id"],
            home=f["teams"]["home"]["name"],
            away_id=f["teams"]["away"]["id"],
            away=f["teams"]["away"]["name"],
            home_score=f["goals"]["home"] or 0,
            away_score=f["goals"]["away"] or 0,
        )
        for f in fixtures[:limit]
    ]


def _minute(t: Dict[str, Any]) -> str:
    return f"{t['elapsed']}+{t['extra']}'" if t.get("extra") else f"{t['elapsed']}'"


def fixture(client: httpx.Client, fixture_id: int) -> Match:
    rows = _get(client, "/fixtures", {"id": fixture_id})
    if not rows:
        raise RuntimeError(f"Fixture {fixture_id} not found.")
    f = rows[0]
    home_id = f["teams"]["home"]["id"]

    def team(side: str) -> Team:
        t = f["teams"][side]
        return Team(id=t["id"], name=t["name"], logo_url=t["logo"], score=f["goals"][side] or 0)

    goals: List[Event] = []
    reds: List[Event] = []
    for e in f.get("events") or []:
        side = "home" if e["team"]["id"] == home_id else "away"
        detail = e.get("detail") or ""
        player = (e.get("player") or {}).get("name") or ""
        if e["type"] == "Goal" and detail != "Missed Penalty":
            # Shootout kicks are logged as goals too; they're not part of the score.
            if e.get("comments") == "Penalty Shootout":
                continue
            note = {"Own Goal": "og", "Penalty": "pen"}.get(detail, "")
            goals.append(Event(_minute(e["time"]), player, side, note))
        elif e["type"] == "Card" and detail in ("Red Card", "Second Yellow card"):
            reds.append(Event(_minute(e["time"]), player, side))

    home, away = team("home"), team("away")
    goals = _fix_own_goal_sides(goals, home.score, away.score)

    pen = f["score"].get("penalty") or {}
    return Match(
        fixture_id=fixture_id,
        date=f["fixture"]["date"][:10],
        competition=f["league"]["name"],
        round=f["league"].get("round") or "",
        venue=(f["fixture"].get("venue") or {}).get("name") or "",
        home=home,
        away=away,
        goals=goals,
        red_cards=reds,
        penalties=f"{pen['home']}-{pen['away']}" if pen.get("home") is not None else None,
    )


def _fix_own_goal_sides(goals: List[Event], home_score: int, away_score: int) -> List[Event]:
    # Whether an own goal's `team` is the scorer's team or the team credited is
    # not documented; the final score settles it.
    def tally(gs: List[Event]) -> tuple:
        return (sum(g.side == "home" for g in gs), sum(g.side == "away" for g in gs))

    if tally(goals) == (home_score, away_score) or not any(g.note == "og" for g in goals):
        return goals
    flipped = [
        Event(g.minute, g.player, "away" if g.side == "home" else "home", g.note) if g.note == "og" else g
        for g in goals
    ]
    return flipped if tally(flipped) == (home_score, away_score) else goals
