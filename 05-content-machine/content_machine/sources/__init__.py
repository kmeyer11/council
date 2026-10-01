"""Source registry. Adding a data provider = one module with
`make_client()`, `recent_finished(client, team_id) -> list[FixtureSummary]`,
`fixture(client, fixture_id) -> Match` and `search_teams(client, name)`
plus one line here."""
from __future__ import annotations

from . import apifootball

SOURCES = {
    "apifootball": apifootball,
}
