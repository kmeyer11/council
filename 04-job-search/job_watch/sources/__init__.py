"""Source registry. Adding a site = one module with
`search(client, keyword, params) -> list[Job]` plus one line here."""
from __future__ import annotations

from . import jobindex, jobnet

SOURCES = {
    "jobindex": jobindex.search,
    "jobnet": jobnet.search,
}
