"""Load settings (config.yaml) plus the search criteria files under criteria/.

Each criteria file is one topic: a `label`, a list of `keywords` (one search
per keyword per source), and optional local filters (`exclude`, `require`, `locations`).
It can narrow `sources`, and pass extra site-specific query parameters under
a key named after the source (e.g. `jobindex: {radius: 30}`). The same
source blocks in config.yaml are defaults for every criteria file; a criteria
file's block is merged on top, key by key. See
../CONTEXT.md and ../templates/criteria.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from .sources import SOURCES


@dataclass
class Criteria:
    label: str
    keywords: List[str]
    exclude: List[str] = field(default_factory=list)
    require: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    source_params: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class Config:
    criteria: List[Criteria]
    max_age_days: int = 21


def _str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(v).strip() for v in value if str(v).strip()]


def _source_blocks(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {s: dict(raw[s]) for s in SOURCES if isinstance(raw.get(s), dict)}


def _load_criteria_file(
    path: Path, default_sources: List[str], default_params: Dict[str, Dict[str, Any]]
) -> Criteria:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = _str_list(raw.get("sources")) or default_sources
    unknown = [s for s in sources if s not in SOURCES]
    if unknown:
        raise ValueError(f"{path.name}: ukendt kilde {unknown}. Kendte: {sorted(SOURCES)}")
    return Criteria(
        label=str(raw.get("label") or path.stem),
        keywords=_str_list(raw.get("keywords")),
        exclude=[e.lower() for e in _str_list(raw.get("exclude"))],
        require=[r.lower() for r in _str_list(raw.get("require"))],
        locations=[loc.lower() for loc in _str_list(raw.get("locations"))],
        sources=sources,
        source_params={
            s: {**default_params.get(s, {}), **_source_blocks(raw).get(s, {})} for s in SOURCES
        },
    )


def load_config(path: Union[str, Path]) -> Config:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    default_sources = _str_list(raw.get("sources")) or sorted(SOURCES)
    default_params = _source_blocks(raw)
    criteria_dir = path.parent / raw.get("criteria_dir", "criteria")

    criteria = [
        _load_criteria_file(f, default_sources, default_params) for f in sorted(criteria_dir.glob("*.yaml"))
    ]
    criteria = [c for c in criteria if c.keywords]
    if not criteria:
        raise ValueError(
            f"Ingen søgekriterier fundet i {criteria_dir}. Kopiér templates/criteria.yaml "
            f"dertil og udfyld 'keywords:' (se CONTEXT.md)."
        )
    return Config(criteria=criteria, max_age_days=int(raw.get("max_age_days", 21)))
