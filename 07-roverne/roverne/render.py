"""source.yaml -> one PNG or PDF per format, next to the yaml.

Every format is laid out on a 1080 px wide canvas. Print formats are then
scaled down to paper size as PDF, so text stays sharp when printed."""
from __future__ import annotations

import base64
import hashlib
import logging
import mimetypes
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import dates
from .config import ROOT, TEMPLATES_DIR, load_brand, load_yaml

log = logging.getLogger("roverne")

WIDTH = 1080
MM_PER_PX = 25.4 / 96  # CSS px

FORMATS: Dict[str, Dict[str, Any]] = {
    "post": {"height": 1350},                                  # Instagram/Facebook 4:5
    "story": {"height": 1920},                                 # story / phone screen 9:16
    "a5": {"height": 1532, "paper_mm": (148, 210)},            # flyer, print
    "a4": {"height": 1527, "paper_mm": (210, 297)},            # poster, print
}


def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    p = p if p.is_absolute() else ROOT / p
    if not p.exists():
        raise FileNotFoundError(f"{path} not found (paths are relative to {ROOT.name}/ or absolute)")
    if p.suffix.lower() == ".heic":
        p = _heic_to_jpg(p)
    return p


def _asset(path: Optional[str]) -> Optional[str]:
    return _resolve(path).as_uri() if path else None


def _inline(path: Optional[str]) -> Optional[str]:
    # CSS masks (the recoloured logo) are fetched with CORS, which file:// URLs fail, so the file goes in as data.
    if not path:
        return None
    p = _resolve(path)
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def _heic_to_jpg(src: Path) -> Path:
    # iPhone photos are HEIC, which Chromium can't show. sips ships with macOS.
    out = ROOT / "photos" / ".converted" / f"{src.stem}-{hashlib.sha1(str(src).encode()).hexdigest()[:8]}.jpg"
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["sips", "-s", "format", "jpeg", str(src), "--out", str(out)],
                       check=True, capture_output=True)
    return out


def build_html(piece: Dict[str, Any], fmt: str) -> str:
    brand = load_brand()
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), undefined=StrictUndefined, autoescape=True)
    env.filters["longdate"] = dates.long_date
    template = env.get_template(f"{piece['type']}/template.html")
    return template.render(
        piece=piece,
        brand=brand,
        fmt=fmt,
        asset=_asset,
        inline=_inline,
        when=dates.when,
        base_css=(TEMPLATES_DIR / "_base.css").as_uri(),
        width=WIDTH,
        height=FORMATS[fmt]["height"],
    )


def _warn_if_past(piece: Dict[str, Any]) -> None:
    if piece.get("starts"):
        start, _ = dates.parse(piece["starts"])
        if start < datetime.now():
            log.warning("starts (%s) is in the past. Wrong year?", piece["starts"])


def render(source_paths: Iterable[Path]) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        browser = pw.chromium.launch()
        for source in source_paths:
            piece = load_yaml(source)
            _warn_if_past(piece)
            name = piece.get("slug") or source.parent.name
            for fmt in piece.get("formats") or ["post"]:
                if fmt not in FORMATS:
                    raise ValueError(f"Unknown format '{fmt}'. Known: {sorted(FORMATS)}")
                spec = FORMATS[fmt]
                # HTML goes to a temp dir: its file:// links point into this workspace, so it's no use in iCloud.
                html = Path(tmp) / f"{name}-{fmt}.html"
                html.write_text(build_html(piece, fmt), encoding="utf-8")
                page = browser.new_page(viewport={"width": WIDTH, "height": spec["height"]})
                page.goto(html.as_uri(), wait_until="networkidle")
                # _layout.html sets this after web fonts load and text is shrunk to fit.
                page.wait_for_function("window.__ready === true", timeout=15000)
                if page.evaluate("window.__overflow"):
                    log.warning("%s: content is taller than the %s canvas and gets cut off. Shorten text or bring, "
                                "or drop this format.", name, fmt)
                if "paper_mm" in spec:
                    w_mm, h_mm = spec["paper_mm"]
                    out = source.with_name(f"{name}-{fmt}.pdf")
                    page.emulate_media(media="screen")
                    page.pdf(path=str(out), width=f"{w_mm}mm", height=f"{h_mm}mm",
                             scale=w_mm / (WIDTH * MM_PER_PX), print_background=True,
                             margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}, page_ranges="1")
                else:
                    out = source.with_name(f"{name}-{fmt}.png")
                    page.screenshot(path=str(out))
                page.close()
                log.info("Rendered %s", out)
        browser.close()
