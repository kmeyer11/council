"""Load search settings (YAML) plus the search criteria they apply to.

Criteria live as one YAML file per topic under `criteria/` (default, next to
config.yaml): each file is a human- or agent-written list of concrete search
terms (specific titles, authors, product names, anything else worth
searching for) under one label. `catalog_ids` / `price_from` / `price_to` /
`order` / `per_page` in config.yaml are defaults every criteria file
inherits; any file can override them (e.g. a different category or price
range) by setting the same keys at its own top level. See ../CONTEXT.md for
how topics/ -> criteria/ is meant to work.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .dedupe import DEFAULT_THRESHOLD


@dataclass
class Watch:
    name: str
    search_text: str
    catalog_ids: Optional[str] = None
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    order: str = "newest_first"
    per_page: int = 48

    def to_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "search_text": self.search_text,
            "order": self.order,
            "per_page": self.per_page,
        }
        if self.catalog_ids:
            params["catalog_ids"] = self.catalog_ids
        if self.price_from is not None:
            params["price_from"] = self.price_from
        if self.price_to is not None:
            params["price_to"] = self.price_to
        return params


@dataclass
class Config:
    domain: str
    watches: List[Watch] = field(default_factory=list)
    dedup_threshold: float = DEFAULT_THRESHOLD


@dataclass
class _Defaults:
    catalog_ids: Optional[str]
    price_from: Optional[float]
    price_to: Optional[float]
    order: str
    per_page: int


def _load_criteria_file(path: Path, defaults: _Defaults) -> tuple[str, List[str], _Defaults]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    label = str(raw.get("label") or path.stem)
    terms = [str(t).strip() for t in (raw.get("terms") or []) if str(t).strip()]

    overrides = _Defaults(
        catalog_ids=str(raw["catalog_ids"]) if raw.get("catalog_ids") else defaults.catalog_ids,
        price_from=raw.get("price_from", defaults.price_from),
        price_to=raw.get("price_to", defaults.price_to),
        order=raw.get("order", defaults.order),
        per_page=raw.get("per_page", defaults.per_page),
    )
    return label, terms, overrides


def load_config(path: Union[str, Path]) -> Config:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    domain = raw.get("domain", "https://www.vinted.dk")
    dedup_threshold = float(raw.get("dedup_threshold", DEFAULT_THRESHOLD))
    defaults = _Defaults(
        catalog_ids=str(raw["catalog_ids"]) if raw.get("catalog_ids") else None,
        price_from=raw.get("price_from"),
        price_to=raw.get("price_to"),
        order=raw.get("order", "newest_first"),
        per_page=raw.get("per_page", 48),
    )

    base_dir = path.parent
    criteria_dir = base_dir / raw.get("criteria_dir", "criteria")

    watches: List[Watch] = []
    for criteria_file in sorted(criteria_dir.glob("*.yaml")):
        label, terms, overrides = _load_criteria_file(criteria_file, defaults)
        for term in terms:
            watches.append(
                Watch(
                    name=f"{label}: {term}",
                    search_text=term,
                    catalog_ids=overrides.catalog_ids,
                    price_from=overrides.price_from,
                    price_to=overrides.price_to,
                    order=overrides.order,
                    per_page=overrides.per_page,
                )
            )

    if not watches:
        raise ValueError(
            f"Ingen søgekriterier fundet i {criteria_dir}. Tilføj en {{navn}}.yaml "
            f"med 'label:' og 'terms:' (se CONTEXT.md)."
        )

    return Config(domain=domain, watches=watches, dedup_threshold=dedup_threshold)
