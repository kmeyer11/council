"""Source registry. Adding a data provider = one module with
`make_client()`, `recent_finished(client, team_id) -> list[FixtureSummary]`,
`fixture(client, fixture_id) -> Match` and `search_teams(client, name)`
plus one line here. Set `HAS_EVENTS = False` if it can't supply goals and
red cards, and `CREST_PREFIX` if its team ids clash with API-Football's."""
from __future__ import annotations

from . import apifootball, footballdata

SOURCES = {
    "apifootball": apifootball,
    "footballdata": footballdata,
}
