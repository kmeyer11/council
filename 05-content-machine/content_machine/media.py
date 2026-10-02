"""Player photos and crests. API-Football abbreviates names ("M. Salah"), so a
scorer is matched to media/{club}/players.yaml by name, alias, or initial + surname."""
from __future__ import annotations

import random
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .config import MEDIA_DIR, ROOT, load_yaml

PHOTO_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def slugify(text: str) -> str:
    text = text.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def load_players(club_slug: str) -> Dict[str, Dict[str, Any]]:
    path = MEDIA_DIR / club_slug / "players.yaml"
    return load_yaml(path) if path.exists() else {}


def _initial_surname(name: str) -> str:
    parts = slugify(name).split("-")
    return f"{parts[0][:1]}-{parts[-1]}" if len(parts) > 1 else parts[0]


def resolve_player(api_name: str, players: Dict[str, Dict[str, Any]]) -> Optional[str]:
    target = slugify(api_name)
    for slug, info in players.items():
        # display is included so names already written into a post.yaml resolve too.
        names = [info.get("name", ""), info.get("display", ""), *(info.get("aliases") or [])]
        if target == slug or target in (slugify(n) for n in names if n):
            return slug
    short = _initial_surname(api_name)
    hits = [slug for slug, info in players.items() if _initial_surname(info.get("name", slug)) == short]
    return hits[0] if len(hits) == 1 else None


def display_name(api_name: str, players: Dict[str, Dict[str, Any]]) -> str:
    slug = resolve_player(api_name, players)
    if slug:
        info = players[slug]
        return info.get("display") or info.get("name") or api_name
    return api_name


def photo_for(club_slug: str, player_slug: str) -> Optional[str]:
    """players/{slug}.jpg, or a random photo from a players/{slug}/ folder."""
    players_dir = MEDIA_DIR / club_slug / "players"
    for ext in PHOTO_EXTS:
        if (players_dir / f"{player_slug}{ext}").exists():
            return str((players_dir / f"{player_slug}{ext}").relative_to(ROOT))
    folder = players_dir / player_slug
    if not folder.is_dir():
        return None
    return _random_photo(club_slug, f"players/{player_slug}")


def _random_photo(club_slug: str, folder: str) -> Optional[str]:
    path = MEDIA_DIR / club_slug / folder
    photos = [p for p in path.iterdir() if p.suffix.lower() in PHOTO_EXTS] if path.is_dir() else []
    return str(random.choice(photos).relative_to(ROOT)) if photos else None


def _default_bg(club_slug: str) -> Optional[str]:
    for ext in PHOTO_EXTS:
        default = MEDIA_DIR / club_slug / f"default-bg{ext}"
        if default.exists():
            return str(default.relative_to(ROOT))
    return None


def outcome(post: Dict[str, Any]) -> str:
    """win | draw | loss for our side. A shootout ("4-3", home-away) decides a level score."""
    ours, theirs = (post["home"], post["away"]) if post["our_side"] == "home" else (post["away"], post["home"])
    a, b = ours["score"], theirs["score"]
    if a == b and post.get("penalties"):
        home, away = (int(x) for x in str(post["penalties"]).split("-"))
        a, b = (home, away) if post["our_side"] == "home" else (away, home)
    return "win" if a > b else "loss" if a < b else "draw"


def _top_scorer_photo(club_slug: str, post: Dict[str, Any]) -> Optional[str]:
    """Photo of whoever scored most for us; a tie is broken at random. Scorers
    without a photo are skipped, so a two-goal scorer with no photo loses to a
    one-goal scorer who has one."""
    players = load_players(club_slug)
    goals = Counter(
        resolve_player(g["player"], players) or slugify(g["player"])
        for g in post.get("goals") or []
        if g["side"] == post["our_side"] and g.get("note") != "og"
    )
    photos = {slug: photo_for(club_slug, slug) for slug in goals}
    with_photo = [slug for slug, photo in photos.items() if photo]
    if not with_photo:
        return None
    best = max(goals[slug] for slug in with_photo)
    return photos[random.choice([slug for slug in with_photo if goals[slug] == best])]


SERIOUS_TYPES = {"breaking-news", "statement"}


def pick_background(post: Dict[str, Any]) -> Optional[str]:
    """Mood-based background for a post. Match result: a loss takes a random
    photo from media/{club}/loss/, a win the top scorer's photo (or a random
    one from victory/ if no scorer has a photo). A draw returns None: the
    user picks that photo by hand.
    Serious announcements take a random photo from serious/. Falls back to the
    club default, else None (the template's club-colour gradient). Other
    announcements return None: their photo is about a specific player."""
    club_slug = post["club"]
    if post["type"] == "match-result":
        result = outcome(post)
        if result == "draw":
            return None
        if result == "loss":
            return _random_photo(club_slug, "loss") or _default_bg(club_slug)
        return _top_scorer_photo(club_slug, post) or _random_photo(club_slug, "victory") or _default_bg(club_slug)
    if post["type"] in SERIOUS_TYPES:
        return _random_photo(club_slug, "serious") or _default_bg(club_slug)
    return None


def cache_crest(team_id: int, url: str, prefix: str = "") -> Optional[str]:
    # Keep the URL's extension: some providers serve SVG crests, and Chromium
    # won't show an SVG saved as .png.
    ext = Path(url.split("?")[0]).suffix.lower() or ".png"
    path = MEDIA_DIR / "crests" / f"{prefix}{team_id}{ext}"
    if not path.exists():
        try:
            resp = httpx.get(url, timeout=20, follow_redirects=True)
            resp.raise_for_status()
        except httpx.HTTPError:
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(resp.content)
    return str(path.relative_to(ROOT))
