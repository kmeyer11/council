"""CLI entry point.

Usage (from the workspace folder):
    python -m roverne.cli new invitation --slug hike-rold-skov
    python -m roverne.cli render "<output_dir>/2026-10-12-invitation-hike-rold-skov/source.yaml"
    python -m roverne.cli photos
"""
from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from .config import ROOT, TEMPLATES_DIR, output_dir
from .render import render

log = logging.getLogger("roverne")

PHOTO_TYPES = {".jpg", ".jpeg", ".png", ".heic", ".webp"}


def slugify(text: str) -> str:
    text = text.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def cmd_new(args) -> None:
    example = TEMPLATES_DIR / args.type / "example.yaml"
    if not example.exists():
        known = sorted(p.parent.name for p in TEMPLATES_DIR.glob("*/example.yaml"))
        raise ValueError(f"Unknown type '{args.type}'. Known: {known}")
    slug = slugify(args.slug)
    day = args.date or date.today().isoformat()
    folder = output_dir() / f"{day}-{args.type}-{slug}"
    path = folder / "source.yaml"
    if path.exists() and not args.force:
        raise FileExistsError(f"{path} exists. Use --force.")
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(example, path)
    text = re.sub(r"(?m)^slug: .*$", f"slug: {slug}", path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")
    print(path)


def cmd_render(args) -> None:
    render([Path(p).expanduser().resolve() for p in args.sources])


def cmd_photos(args) -> None:
    # Lets the agent pick a photo by folder and file name without opening images.
    photos = ROOT / "photos"
    for p in sorted(photos.rglob("*")):
        # .converted/ holds the JPGs made from HEIC, not photos to pick from.
        if p.suffix.lower() in PHOTO_TYPES and not p.relative_to(photos).parts[0].startswith("."):
            print(p.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Make media for Røverne.")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="Start a piece from a template's example.yaml in the output folder.")
    p.add_argument("type")
    p.add_argument("--slug", required=True)
    p.add_argument("--date", help="yyyy-mm-dd for the folder name, default today.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("render", help="Render one or more source.yaml files to PNG/PDF next to them.")
    p.add_argument("sources", nargs="+")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("photos", help="List photos in photos/.")
    p.set_defaults(func=cmd_photos)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        args.func(args)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        log.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
