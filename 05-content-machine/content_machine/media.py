"""Player photos and crests. API-Football abbreviates names ("M. Salah"), so a
scorer is matched to media/{club}/players.yaml by name, alias, or initial + surname."""
from __future__ import annotations

import re
import unicodedata
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
        names = [info.get("name", ""), *(info.get("aliases") or [])]
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
    """players/{slug}.jpg, or the first photo in a players/{slug}/ folder."""
    players_dir = MEDIA_DIR / club_slug / "players"
    for ext in PHOTO_EXTS:
        if (players_dir / f"{player_slug}{ext}").exists():
            return str((players_dir / f"{player_slug}{ext}").relative_to(ROOT))
    folder = players_dir / player_slug
    if not folder.is_dir():
        return None
    photos = sorted(p for p in folder.iterdir() if p.suffix.lower() in PHOTO_EXTS)
    return str(photos[0].relative_to(ROOT)) if photos else None


def pick_background(club_slug: str, scorer_names: List[str]) -> Optional[str]:
    """First of our scorers who has a photo, else the club default, else None
    (the template then falls back to a gradient in club colours)."""
    players = load_players(club_slug)
    for name in scorer_names:
        slug = resolve_player(name, players) or slugify(name)
        photo = photo_for(club_slug, slug)
        if photo:
            return photo
    for ext in PHOTO_EXTS:
        default = MEDIA_DIR / club_slug / f"default-bg{ext}"
        if default.exists():
            return str(default.relative_to(ROOT))
    return None


def cache_crest(team_id: int, url: str) -> Optional[str]:
    path = MEDIA_DIR / "crests" / f"{team_id}.png"
    if not path.exists():
        try:
            resp = httpx.get(url, timeout=20, follow_redirects=True)
            resp.raise_for_status()
        except httpx.HTTPError:
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(resp.content)
    return str(path.relative_to(ROOT))
