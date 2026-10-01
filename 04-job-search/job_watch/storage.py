"""SQLite-backed 'seen jobs' store so runs only report new postings."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

from .models import Job, fingerprint


class SeenStore:
    def __init__(self, db_path: Union[str, Path] = "job_watch.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_jobs (
                job_key TEXT PRIMARY KEY,
                fingerprint TEXT NOT NULL,
                label TEXT NOT NULL,
                title TEXT,
                company TEXT,
                url TEXT,
                first_seen TEXT NOT NULL
            )
            """
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprint ON seen_jobs(fingerprint)")
        self._conn.commit()

    def is_new(self, job: Job) -> bool:
        return self._conn.execute("SELECT 1 FROM seen_jobs WHERE job_key = ?", (job.key,)).fetchone() is None

    def is_duplicate(self, job: Job) -> bool:
        return (
            self._conn.execute("SELECT 1 FROM seen_jobs WHERE fingerprint = ?", (fingerprint(job),)).fetchone()
            is not None
        )

    def mark_seen(self, job: Job, label: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO seen_jobs (job_key, fingerprint, label, title, company, url, first_seen) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                job.key,
                fingerprint(job),
                label,
                job.title,
                job.company,
                job.url,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "SeenStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
