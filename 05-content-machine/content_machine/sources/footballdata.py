"""football-data.org v4. Docs: https://www.football-data.org/documentation/api
Auth header `X-Auth-Token`, free key from https://www.football-data.org/client/register.

The free plan serves the current season, but only score, date, competition and
round: goals, bookings and venue come back null, and domestic cups (DFB-Pokal)
aren't covered. So `match` writes the post without goals and red
cards (HAS_EVENTS) and someone fills those in from two other sources.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import httpx

from ..models import FixtureSummary, Match, Team

BASE_URL = "https://api.football-data.org/v4"
HAS_EVENTS = False
# Team ids differ from API-Football's, so crests are cached under their own names.
CREST_PREFIX = "fd-"
# No team search endpoint; these are the free competitions our clubs play in.
SEARCH_COMPETITIONS = ("BL1", "CL")

# Written the way API-Football names rounds, so cli._round and the club yaml's
# round_names work the same for both sources.
_STAGES = {
    "REGULAR_SEASON": "Regular Season",
    "LEAGUE_STAGE": "League Stage",
    "PLAYOFFS": "Knockout Round Play-offs",
    "LAST_16": "Round of 16",
    "QUARTER_FINALS": "Quarter-finals",
    "SEMI_FINALS": "Semi-finals",
    "FINAL": "Final",
}


def make_client() -> httpx.Client:
    key = os.environ.get("FOOTBALL_DATA_KEY")
    if not key:
        raise RuntimeError("FOOTBALL_DATA_KEY missing - put it in .env (see .env.example).")
    return httpx.Client(base_url=BASE_URL, headers={"X-Auth-Token": key}, timeout=20)


def _get(client: httpx.Client, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    resp = client.get(path, params=params or {})
    if resp.status_code == 429:  # free plan: 10 requests/minute
        time.sleep(int(resp.headers.get("Retry-After", "6")))
        resp = client.get(path, params=params or {})
    if resp.status_code == 403:
        raise RuntimeError(f"football-data.org {path}: not in the free plan (domestic cups like the DFB-Pokal aren't).")
    resp.raise_for_status()
    return resp.json()


def _name(t: Dict[str, Any]) -> str:
    return t.get("shortName") or t["name"]


def _scores(m: Dict[str, Any]) -> tuple:
    s = m["score"]
    # After a shootout, fullTime includes the shootout goals.
    if s.get("duration") == "PENALTY_SHOOTOUT" and s.get("regularTime"):
        extra = s.get("extraTime") or {}
        return (
            s["regularTime"]["home"] + (extra.get("home") or 0),
            s["regularTime"]["away"] + (extra.get("away") or 0),
        )
    return s["fullTime"]["home"] or 0, s["fullTime"]["away"] or 0


def _round(m: Dict[str, Any]) -> str:
    stage = _STAGES.get(m.get("stage") or "", (m.get("stage") or "").replace("_", " ").title())
    if m.get("stage") in ("REGULAR_SEASON", "LEAGUE_STAGE") and m.get("matchday"):
        return f"{stage} - {m['matchday']}"
    return stage


def competition_teams(client: httpx.Client, code: str) -> List[Dict[str, Any]]:
    """Every team in a competition this season, e.g. code "BL1"."""
    return [{"id": t["id"], "name": t["name"], "short_name": t.get("shortName", ""), "logo": t["crest"],
             "country": (t.get("area") or {}).get("name", "")}
            for t in _get(client, f"/competitions/{code}/teams").get("teams", [])]


def search_teams(client: httpx.Client, name: str) -> List[Dict[str, Any]]:
    seen: Dict[int, Dict[str, Any]] = {}
    for code in SEARCH_COMPETITIONS:
        for t in competition_teams(client, code):
            if name.lower() in f"{t['name']} {t['short_name']}".lower():
                seen[t["id"]] = t
    return list(seen.values())


def recent_finished(client: httpx.Client, team_id: int, limit: int = 5) -> List[FixtureSummary]:
    """Newest first. Only covers free-plan competitions, so a cup game can be missing."""
    matches = _get(client, f"/teams/{team_id}/matches", {"status": "FINISHED"}).get("matches", [])
    if not matches:
        raise RuntimeError(f"No finished matches this season for team {team_id}.")
    matches.sort(key=lambda m: m["utcDate"], reverse=True)
    out = []
    for m in matches[:limit]:
        home_score, away_score = _scores(m)
        out.append(FixtureSummary(
            id=m["id"],
            date=m["utcDate"][:10],
            competition=m["competition"]["name"],
            home_id=m["homeTeam"]["id"],
            home=_name(m["homeTeam"]),
            away_id=m["awayTeam"]["id"],
            away=_name(m["awayTeam"]),
            home_score=home_score,
            away_score=away_score,
        ))
    return out


def fixture(client: httpx.Client, fixture_id: int) -> Match:
    m = _get(client, f"/matches/{fixture_id}")
    home_score, away_score = _scores(m)
    pen = m["score"].get("penalties") or {}

    def team(t: Dict[str, Any], score: int) -> Team:
        return Team(id=t["id"], name=_name(t), logo_url=t.get("crest") or "", score=score)

    return Match(
        fixture_id=fixture_id,
        date=m["utcDate"][:10],
        competition=m["competition"]["name"],
        round=_round(m),
        venue=m.get("venue") or "",
        home=team(m["homeTeam"], home_score),
        away=team(m["awayTeam"], away_score),
        penalties=f"{pen['home']}-{pen['away']}" if pen.get("home") is not None else None,
    )
