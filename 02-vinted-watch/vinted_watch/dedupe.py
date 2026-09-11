"""Near-duplicate title detection.

The same physical book often gets listed by multiple sellers under a
slightly different title (different punctuation, edition note, a word
dropped or added). Each listing has its own Vinted item id, so id-based
"seen" tracking alone treats every one as a brand new match. This catches
those before they're reported/favourited, biased toward fewer, more precise
hits over catching every possible listing.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Iterable

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_WS = re.compile(r"\s+")

DEFAULT_THRESHOLD = 0.84


def normalize_title(title: str) -> str:
    t = title.lower()
    t = _PUNCT.sub(" ", t)
    t = _WS.sub(" ", t).strip()
    return t


def is_near_duplicate(
    title: str, seen_normalized_titles: Iterable[str], threshold: float = DEFAULT_THRESHOLD
) -> bool:
    """seen_normalized_titles must already be normalize_title()'d."""
    candidate = normalize_title(title)
    if not candidate:
        return False
    for other in seen_normalized_titles:
        if SequenceMatcher(None, candidate, other).ratio() >= threshold:
            return True
    return False
