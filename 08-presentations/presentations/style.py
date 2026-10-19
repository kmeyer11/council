"""Paths, and reading a style.md: YAML front matter (what the renderer uses)
followed by a Markdown body (what the agent reads before writing slides)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
STYLES_DIR = ROOT / "styles"
DECKS_DIR = ROOT / "decks"
SAMPLE_DECK = ROOT / "presentations" / "sample.yaml"

REQUIRED_COLORS = ("background", "surface", "text", "muted", "primary", "on_primary", "accent")

DEFAULTS: Dict[str, Any] = {
    "fonts": {"heading": "Georgia", "body": "Arial"},
    "sizes": {"cover": 48, "title": 34, "heading": 22, "body": 18, "caption": 12, "stat": 60},
    "motif": "none",
    "footer": "",
    "slide_numbers": True,
    "logo": None,
}


def split_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("style.md must start with a '---' YAML front matter block.")
    head, sep, body = text[4:].partition("\n---\n")
    if not sep:
        raise ValueError("style.md front matter has no closing '---'.")
    return yaml.safe_load(head) or {}, body


def load_style(path: Path) -> Dict[str, Any]:
    tokens, _ = split_front_matter(path.read_text(encoding="utf-8"))
    style = {**DEFAULTS, **tokens}
    for key in ("fonts", "sizes"):
        style[key] = {**DEFAULTS[key], **(tokens.get(key) or {})}
    colors = {k: str(v).lstrip("#").upper() for k, v in (tokens.get("colors") or {}).items()}
    missing = [c for c in REQUIRED_COLORS if c not in colors]
    if missing:
        raise ValueError(f"{path}: colors is missing {missing}.")
    # Column headings sit on `surface`; primary only reads there when the style is light.
    colors.setdefault("heading", colors["primary"])
    style["colors"] = colors
    style["dir"] = path.parent
    return style


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
