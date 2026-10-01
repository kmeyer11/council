from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    source: str
    id: str
    title: str
    company: str
    location: str
    url: str
    published: Optional[datetime]

    @property
    def key(self) -> str:
        return f"{self.source}:{self.id}"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"[^\wæøå]+", " ", text).strip()


def fingerprint(job: Job) -> str:
    """Same posting on two sites gets the same fingerprint (exact title +
    company after normalizing). Deliberately strict: a missed cross-site
    duplicate costs one extra CSV row, a false match hides a real job."""
    return f"{normalize(job.title)}|{normalize(job.company)}"
