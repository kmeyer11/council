"""Paths, .env and club files. Every path stored in a post.yaml or club yaml is
relative to the workspace root (ROOT), so posts can be re-rendered from anywhere."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parent.parent
CLUBS_DIR = ROOT / "clubs"
TEMPLATES_DIR = ROOT / "templates"
MEDIA_DIR = ROOT / "media"
POSTS_DIR = ROOT / "posts"


def load_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_club(slug: str) -> Dict[str, Any]:
    path = CLUBS_DIR / f"{slug}.yaml"
    if not path.exists():
        known = sorted(p.stem for p in CLUBS_DIR.glob("*.yaml"))
        raise ValueError(f"Unknown club '{slug}'. Known: {known}")
    club = load_yaml(path)
    club["slug"] = slug
    return club
