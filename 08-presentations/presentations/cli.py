"""CLI entry point.

Usage (from the workspace folder):
    python -m presentations.cli styles
    python -m presentations.cli new --style bold --slug kvartalsmoede
    python -m presentations.cli render decks/2026-10-19-kvartalsmoede/deck.yaml
    python -m presentations.cli sample bold
"""
from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

from .render import build, preview
from .style import DECKS_DIR, OUTPUT_DIR, SAMPLE_DECK, STYLES_DIR, load_style, split_front_matter

log = logging.getLogger("presentations")

THIS_DECK = """
## This deck

Filled in when the deck is made, and added to whenever a choice is made
while building it. Read this before adding slides later.

- Purpose: {fill in: what the talk is for, e.g. a decision, an update, a pitch}
- Audience: {fill in}
- Language: {fill in: da or en}
- Length: {fill in: minutes, so roughly how many slides}
- Theme and imagery: {fill in: the topic's visual idea, which photos, where they're from}
- Decisions: {add as you go: e.g. "titles are full sentences", "one stat per slide"}
"""

STARTER_DECK = """# Slides for this deck. Layouts and their fields: presentations/sample.yaml.
# Images go in images/ next to this file. Edit here, then render; never edit
# the .pptx by hand (the next render refuses to overwrite it, or loses it).
title: {title}
author: ""
slug: {slug}
slides:
  - layout: title
    title: {title}
    subtitle: ""
    byline: ""

  - layout: closing
    title: Tak
"""


def slugify(text: str) -> str:
    text = text.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def style_dir(name: str) -> Path:
    folder = STYLES_DIR / name
    if not (folder / "style.md").exists():
        known = sorted(p.parent.name for p in STYLES_DIR.glob("*/style.md"))
        raise ValueError(f"Unknown style '{name}'. Known: {known}")
    return folder


def copy_style(name: str, dest: Path, stamp: str) -> None:
    """Freeze the style into the deck folder, so later changes to the style don't move old decks."""
    for item in style_dir(name).iterdir():
        if item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
        else:
            shutil.copy(item, dest / item.name)
    path = dest / "style.md"
    text = path.read_text(encoding="utf-8")
    split_front_matter(text)  # fail early on a broken style
    text = text.replace("---\n", f"---\nbased_on: {name}  # copied {stamp}; edit this copy, not styles/{name}\n", 1)
    path.write_text(text.rstrip() + "\n" + THIS_DECK, encoding="utf-8")


def show_result(pptx: Path, deck_dir: Path, no_preview: bool) -> None:
    print(pptx)
    if not no_preview:
        for png in preview(pptx, deck_dir / "preview"):
            print(png)


def cmd_styles(args) -> None:
    for path in sorted(STYLES_DIR.glob("*/style.md")):
        style = load_style(path)
        print(f"{path.parent.name:16} {style.get('description', '')}")


def cmd_new(args) -> None:
    slug = slugify(args.slug)
    day = args.date or date.today().isoformat()
    folder = DECKS_DIR / f"{day}-{slug}"
    if folder.exists() and not args.force:
        raise FileExistsError(f"{folder} exists. Use --force.")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "images").mkdir(exist_ok=True)
    copy_style(args.style, folder, day)
    deck_title = args.title or args.slug
    (folder / "deck.yaml").write_text(STARTER_DECK.format(title=deck_title, slug=slug), encoding="utf-8")
    print(folder / "deck.yaml")
    print(folder / "style.md")


def cmd_render(args) -> None:
    for deck in args.decks:
        path = Path(deck).expanduser().resolve()
        if path.is_dir():
            path = path / "deck.yaml"
        show_result(build(path, OUTPUT_DIR, force=args.force), path.parent, args.no_preview)


def sample_image(path: Path, colors: dict) -> None:
    """A flat stand-in photo in the style's colours, so the sample shows the image layouts."""
    img = Image.new("RGB", (1600, 1200), "#" + colors["surface"])
    draw = ImageDraw.Draw(img)
    draw.ellipse((700, 150, 1500, 950), fill="#" + colors["primary"])
    draw.ellipse((250, 600, 750, 1100), fill="#" + colors["accent"])
    img.save(path)


def cmd_sample(args) -> None:
    folder = DECKS_DIR / "_samples" / args.style
    shutil.rmtree(folder, ignore_errors=True)
    (folder / "images").mkdir(parents=True)
    copy_style(args.style, folder, date.today().isoformat())
    shutil.copy(SAMPLE_DECK, folder / "deck.yaml")
    sample_image(folder / "images" / "sample.png", load_style(folder / "style.md")["colors"])
    show_result(build(folder / "deck.yaml", folder, force=True), folder, args.no_preview)


def main() -> None:
    parser = argparse.ArgumentParser(description="Make PowerPoint decks in a saved style.")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("styles", help="List the saved styles.")
    p.set_defaults(func=cmd_styles)

    p = sub.add_parser("new", help="Start a deck in decks/ with its own copy of a style.")
    p.add_argument("--style", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--title")
    p.add_argument("--date", help="yyyy-mm-dd for the folder name, default today.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("render", help="Build the .pptx on the Desktop from deck.yaml + style.md, and preview PNGs.")
    p.add_argument("decks", nargs="+", help="deck.yaml files or deck folders")
    p.add_argument("--no-preview", action="store_true")
    p.add_argument("--force", action="store_true", help="Overwrite a .pptx that was edited by hand.")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("sample", help="Render every layout in a style, to judge the style.")
    p.add_argument("style")
    p.add_argument("--no-preview", action="store_true")
    p.set_defaults(func=cmd_sample)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    try:
        args.func(args)
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        log.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
