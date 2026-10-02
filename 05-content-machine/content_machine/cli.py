"""CLI entry point.

Usage (from the workspace folder):
    python -m content_machine.cli match --club vfb [--fixture ID --yes] [--force]
    python -m content_machine.cli new transfer --club vfb --slug undav-verlaengerung
    python -m content_machine.cli render posts/vfb/2026-09-27-match-result-bayern/post.yaml
    python -m content_machine.cli background posts/vfb/2026-09-27-match-result-bayern/post.yaml
    python -m content_machine.cli teams --search Stuttgart
    python -m content_machine.cli crest --search Freiburg
    python -m content_machine.cli crests --competition BL1
"""
from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import media
from .config import POSTS_DIR, ROOT, TEMPLATES_DIR, load_club, load_env, load_yaml
from .models import Event, FixtureSummary, Match
from .render import render
from .sources import SOURCES

log = logging.getLogger("content_machine")


def _source(club: Dict[str, Any]):
    api = club.get("api") or {}
    name = api.get("source", "apifootball")
    if name not in SOURCES:
        raise ValueError(f"Unknown source '{name}'. Known: {sorted(SOURCES)}")
    if not api.get("team_id"):
        raise ValueError(
            f"clubs/{club['slug']}.yaml has no api.team_id. Find it with: "
            f"python -m content_machine.cli teams --search \"{club.get('name', '')}\""
        )
    return SOURCES[name], int(api["team_id"])


def _round(raw: str, club: Dict[str, Any]) -> str:
    # API-Football: "Regular Season - 10", "Relegation Round - 10", "Quarter-finals".
    names = club.get("round_names") or {}
    if raw in names:
        return names[raw]
    m = re.match(r"(.+) - (\d+)$", raw)
    if not m:
        return raw
    if m.group(1) == "Regular Season":
        return club.get("strings", {}).get("round", "Round {n}").format(n=m.group(2))
    return names[m.group(1)].format(n=m.group(2)) if m.group(1) in names else raw


def _name(team_id: int, api_name: str, club: Dict[str, Any], our_id: int) -> str:
    if team_id == our_id:
        return club.get("short_name") or club["name"]
    return (club.get("team_names") or {}).get(api_name, api_name)


def _team_name(team, club: Dict[str, Any], our_id: int) -> str:
    return _name(team.id, team.name, club, our_id)


def _events(events: List[Event], players_by_side: Dict[str, Dict]) -> List[Dict[str, str]]:
    out = []
    for e in events:
        # Own goals are credited to one side but scored by the other side's player.
        roster_side = ("away" if e.side == "home" else "home") if e.note == "og" else e.side
        name = media.display_name(e.player, players_by_side[roster_side])
        out.append({"minute": e.minute, "player": name, "side": e.side, "note": e.note})
    return out


def match_to_post(match: Match, club: Dict[str, Any], our_id: int, crest_prefix: str = "") -> Dict[str, Any]:
    our_side = "home" if match.home.id == our_id else "away"
    ours = media.load_players(club["slug"])
    players_by_side = {our_side: ours, ("away" if our_side == "home" else "home"): {}}

    def team(t) -> Dict[str, Any]:
        crest = club.get("logo") if t.id == our_id and club.get("logo") else media.cache_crest(t.id, t.logo_url, crest_prefix)
        return {"name": _team_name(t, club, our_id), "crest": crest, "score": t.score}

    post = {
        "type": "match-result",
        "club": club["slug"],
        "fixture_id": match.fixture_id,
        "date": match.date,
        "competition": (club.get("competition_names") or {}).get(match.competition, match.competition),
        "round": _round(match.round, club),
        "venue": match.venue,
        "our_side": our_side,
        "home": team(match.home),
        "away": team(match.away),
        "penalties": match.penalties,
        "goals": _events(match.goals, players_by_side),
        "red_cards": _events(match.red_cards, players_by_side),
    }
    post["background"] = media.pick_background(post)
    return post


def _write_post(post: Dict[str, Any], folder: Path, force: bool) -> Path:
    path = folder / "post.yaml"
    if path.exists() and not force:
        raise FileExistsError(f"{path.relative_to(ROOT)} exists (may hold manual edits). Use --force, or `render` it.")
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(post, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _print_recent(recent: List[FixtureSummary], club: Dict[str, Any], our_id: int) -> None:
    print("\nMost recent finished matches:")
    for i, f in enumerate(recent, 1):
        home, away = _name(f.home_id, f.home, club, our_id), _name(f.away_id, f.away, club, our_id)
        print(f"  {i}. {f.date}  {home} {f.home_score}-{f.away_score} {away}  ({f.competition})  [fixture {f.id}]")


def _confirmed_match(source, client, club: Dict[str, Any], team_id: int, fixture_id, assume_yes: bool) -> Match:
    """Human checkpoint: nothing is written until someone confirms this is the
    right game (the API's "latest" can be a friendly, a postponed fixture, or stale)."""
    recent = None
    if fixture_id is None:
        recent = source.recent_finished(client, team_id)
        fixture_id = recent[0].id
    while True:
        match = source.fixture(client, fixture_id)
        home, away = _team_name(match.home, club, team_id), _team_name(match.away, club, team_id)
        pens = f" ({match.penalties} pens)" if match.penalties else ""
        print(f"\nFetched: {match.date}  {home} {match.home.score}-{match.away.score} {away}{pens}"
              f"  ({match.competition}, {match.round})  [fixture {match.fixture_id}]")
        if assume_yes:
            return match
        if not sys.stdin.isatty():
            _print_recent(recent or source.recent_finished(client, team_id), club, team_id)
            raise RuntimeError("Not confirmed, nothing written. Check the match above with the user, "
                               "then rerun with --fixture ID --yes.")
        if input("Is this the right match? [y/N] ").strip().lower() in ("y", "yes", "j", "ja"):
            return match
        recent = recent or source.recent_finished(client, team_id)
        _print_recent(recent, club, team_id)
        pick = input("Pick a number, or press Enter to cancel: ").strip()
        if not (pick.isdigit() and 1 <= int(pick) <= len(recent)):
            raise RuntimeError("Cancelled, nothing written. An older match can be fetched with --fixture ID.")
        fixture_id = recent[int(pick) - 1].id


def cmd_match(args) -> None:
    club = load_club(args.club)
    source, team_id = _source(club)
    with source.make_client() as client:
        match = _confirmed_match(source, client, club, team_id, args.fixture, args.yes)
    post = match_to_post(match, club, team_id, getattr(source, "CREST_PREFIX", ""))
    opponent = post["away"] if post["our_side"] == "home" else post["home"]
    folder = POSTS_DIR / club["slug"] / f"{post['date']}-match-{media.slugify(opponent['name'])}"
    path = _write_post(post, folder, args.force)
    log.info("Wrote %s", path.relative_to(ROOT))
    if not getattr(source, "HAS_EVENTS", True):
        # A rendered PNG without goals looks finished, so stop before rendering.
        log.warning("This source has no goals or red cards. Fill them in (and background:) "
                    "from two sources, then run: render %s", path.relative_to(ROOT))
        return
    if _is_draw(post):
        log.warning(DRAW_MSG, path.relative_to(ROOT))
        return
    if not args.no_render:
        render([path])


def cmd_new(args) -> None:
    example = TEMPLATES_DIR / args.type / "example.yaml"
    if not example.exists():
        known = sorted(p.parent.name for p in TEMPLATES_DIR.glob("*/example.yaml"))
        raise ValueError(f"Unknown post type '{args.type}'. Known: {known}")
    load_club(args.club)
    day = args.date or date.today().isoformat()
    folder = POSTS_DIR / args.club / f"{day}-{args.type}-{media.slugify(args.slug)}"
    path = folder / "post.yaml"
    if path.exists() and not args.force:
        raise FileExistsError(f"{path.relative_to(ROOT)} exists. Use --force.")
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(example, path)
    text = re.sub(r"(?m)^club: .*$", f"club: {args.club}", path.read_text(encoding="utf-8"))
    text = re.sub(r"(?m)^date: .*$", f'date: "{day}"', text)
    path.write_text(text, encoding="utf-8")
    # A match post's example score is placeholder data, so its background is
    # picked by `background` once the real score and goals are filled in.
    if args.type != "match-result":
        _set_background(path)
    print(path.relative_to(ROOT))


def _is_draw(post: Dict[str, Any]) -> bool:
    return post["type"] == "match-result" and media.outcome(post) == "draw"


DRAW_MSG = "Draw: the user picks the background. Set background: in %s by hand, then render."


def _set_background(path: Path) -> Optional[str]:
    # Rewrites only the background line so the template's comments survive.
    post = load_yaml(path)
    if _is_draw(post):
        # Leave the line alone so a photo the user already chose survives a rerun.
        log.warning(DRAW_MSG, path.relative_to(ROOT))
        return post.get("background")
    bg = media.pick_background(post)
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^background:[^#\n]*?(\s*#|$)", lambda m: f"background: {bg or 'null'}{m.group(1)}", text, count=1)
    path.write_text(text, encoding="utf-8")
    return bg


def cmd_background(args) -> None:
    for p in args.posts:
        path = Path(p).resolve()
        bg = _set_background(path)
        if not _is_draw(load_yaml(path)):
            print(bg or "null (no photo found, the template uses the club gradient)")


def cmd_render(args) -> None:
    render([Path(p).resolve() for p in args.posts])


def cmd_crest(args) -> None:
    # Team search works on the free API-Football plan, so crests are available
    # even when match data has to be looked up by hand.
    source = SOURCES[args.source]
    with source.make_client() as client:
        teams = source.search_teams(client, args.search)
    if not teams:
        raise RuntimeError(f"No team found for '{args.search}'. Try `teams --search` with another spelling.")
    exact = [t for t in teams if t["name"].lower() == args.search.lower()]
    if args.id:
        team = next((t for t in teams if t["id"] == args.id), None)
    elif len(teams) == 1 or len(exact) == 1:
        team = exact[0] if exact else teams[0]
    else:
        team = None
    if team is None:
        for t in teams:
            print(f"{t['id']:>6}  {t['name']}  ({t.get('country', '')})")
        raise RuntimeError("Several teams match. Rerun with --id.")
    print(media.cache_crest(team["id"], team["logo"], getattr(source, "CREST_PREFIX", "")))


def cmd_crests(args) -> None:
    # Only football-data.org lists a competition's teams on its free plan.
    source = SOURCES["footballdata"]
    with source.make_client() as client:
        teams = source.competition_teams(client, args.competition)
    for t in teams:
        path = media.cache_crest(t["id"], t["logo"], source.CREST_PREFIX)
        print(f"{t['id']:>6}  {t['name']:<28}  {path or 'download failed'}")


def cmd_teams(args) -> None:
    source = SOURCES[args.source]
    with source.make_client() as client:
        for t in source.search_teams(client, args.search):
            print(f"{t['id']:>6}  {t['name']}  ({t.get('country', '')})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Instagram post graphics per club.")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("match", help="Fetch a finished match and render its result graphic.")
    p.add_argument("--club", required=True)
    p.add_argument("--fixture", type=int, help="Fixture id (default: club's most recent finished match).")
    p.add_argument("--force", action="store_true", help="Overwrite an existing post.yaml.")
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--yes", action="store_true", help="Skip the 'right match?' check (only once a human has confirmed).")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("new", help="Start a post from a template's example.yaml.")
    p.add_argument("type")
    p.add_argument("--club", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--date", help="yyyy-mm-dd, default today. For a match post: the match day.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("render", help="Render one or more post.yaml files to post.png.")
    p.add_argument("posts", nargs="+")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("background", help="Pick a background from the post's result or type and write it to post.yaml.")
    p.add_argument("posts", nargs="+")
    p.set_defaults(func=cmd_background)

    p = sub.add_parser("crest", help="Download a team's crest to media/crests/ and print its path.")
    p.add_argument("--search", required=True)
    p.add_argument("--id", type=int, help="Pick one team when the search matches several.")
    p.add_argument("--source", default="apifootball", choices=sorted(SOURCES))
    p.set_defaults(func=cmd_crest)

    p = sub.add_parser("crests", help="Download every crest in a football-data.org competition (e.g. BL1).")
    p.add_argument("--competition", required=True)
    p.set_defaults(func=cmd_crests)

    p = sub.add_parser("teams", help="Look up a team id for clubs/*.yaml.")
    p.add_argument("--search", required=True)
    p.add_argument("--source", default="apifootball", choices=sorted(SOURCES))
    p.set_defaults(func=cmd_teams)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one INFO line per request is noise
    load_env()
    try:
        args.func(args)
    except (ValueError, FileExistsError, RuntimeError) as exc:
        log.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
