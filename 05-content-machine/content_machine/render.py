"""post.yaml -> post.html -> post.png. The HTML is written next to the PNG so
file:// images resolve and the layout can be opened in a browser to tweak."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .config import ROOT, TEMPLATES_DIR, load_club, load_yaml

log = logging.getLogger("content_machine")

WIDTH, HEIGHT = 1080, 1350  # Instagram 4:5 portrait

MONTHS = {
    "da": ["januar", "februar", "marts", "april", "maj", "juni", "juli",
           "august", "september", "oktober", "november", "december"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}


def _asset(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    p = Path(path)
    p = p if p.is_absolute() else ROOT / p
    return p.as_uri() if p.exists() else None


def _long_date(value: Any, lang: str) -> str:
    y, m, d = (int(x) for x in str(value)[:10].split("-"))
    month = MONTHS.get(lang, MONTHS["en"])[m - 1]
    return f"{d}. {month} {y}" if lang == "da" else f"{d} {month} {y}"


def build_html(post: Dict[str, Any]) -> str:
    club = load_club(post["club"])
    lang = club.get("language", "en")
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), undefined=StrictUndefined, autoescape=True)
    env.filters["longdate"] = lambda v: _long_date(v, lang)
    template = env.get_template(f"{post['type']}/template.html")
    return template.render(
        post=post,
        club=club,
        s=club.get("strings", {}),
        asset=_asset,
        base_css=(TEMPLATES_DIR / "_base.css").as_uri(),
        width=WIDTH,
        height=HEIGHT,
    )


def render(post_paths: Iterable[Path]) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
        for post_path in post_paths:
            post = load_yaml(post_path)
            html_path = post_path.with_name("post.html")
            html_path.write_text(build_html(post), encoding="utf-8")
            page.goto(html_path.as_uri(), wait_until="networkidle")
            # _layout.html sets this after web fonts load and text is shrunk to fit.
            page.wait_for_function("window.__ready === true", timeout=15000)
            png = post_path.with_name("post.png")
            page.screenshot(path=str(png))
            log.info("Rendered %s", png.relative_to(ROOT) if png.is_relative_to(ROOT) else png)
        browser.close()
