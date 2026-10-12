"""Paths and yaml loading. Paths inside a source.yaml or brand.yaml are relative
to media_dir (the user's photo folder), then the workspace root (ROOT), or absolute,
so a piece can be re-rendered from anywhere."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
BRAND_FILE = ROOT / "brand" / "brand.yaml"


def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_brand() -> Dict[str, Any]:
    return load_yaml(BRAND_FILE)


def output_dir() -> Path:
    value = load_yaml(ROOT / "config.yaml").get("output_dir")
    if not value:
        raise ValueError("config.yaml has no output_dir. Set it to the iCloud folder the media should go in.")
    return Path(value).expanduser()


def media_dir() -> Path:
    value = load_yaml(ROOT / "config.yaml").get("media_dir")
    if not value:
        raise ValueError("config.yaml has no media_dir. Set it to the folder the photos and logos are in.")
    return Path(value).expanduser()
