"""CLI entry point: search every source for every criteria keyword once and
report postings not seen before.

Usage:
    python -m job_watch.cli --config config/config.yaml --csv state/jobs.csv --db state/job_watch.db
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

import httpx

from .config import Criteria, load_config
from .models import Job
from .sources import SOURCES
from .storage import SeenStore

log = logging.getLogger("job_watch")


def _write_csv(csv_path: str, new_jobs: List[Tuple[str, Job]]) -> None:
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    write_header = not Path(csv_path).exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["found", "label", "source", "title", "company", "location", "published", "url"])
        found = datetime.now().strftime("%Y-%m-%d")
        for label, job in new_jobs:
            published = job.published.strftime("%Y-%m-%d") if job.published else ""
            writer.writerow([found, label, job.source, job.title, job.company, job.location, published, job.url])


def _title_has(title: str, term: str) -> bool:
    # Danish compounds ("softwareudvikler") need substring matching, but short
    # terms like "it"/"qa"/"bi" would then hit inside ordinary words
    # ("kvalitet"), so those must stand alone.
    if len(term) <= 3:
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", title) is not None
    return term in title


def _passes_filters(job: Job, criteria: Criteria, cutoff: datetime) -> bool:
    if job.published and job.published < cutoff:
        return False
    title = job.title.lower()
    if any(_title_has(title, word) for word in criteria.exclude):
        return False
    # Both sites match loosely (Jobnet splits "it-medarbejder" and effectively
    # searches "medarbejder"; Jobindex matches boilerplate anywhere in the ad),
    # so the title itself must show the job is on-topic.
    if criteria.require and not any(_title_has(title, word) for word in criteria.require):
        return False
    if criteria.locations:
        location = job.location.lower()
        if not any(loc in location for loc in criteria.locations):
            return False
    return True


def run_once(config_path: str, db_path: str, csv_path: Optional[str]) -> int:
    config = load_config(config_path)
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.max_age_days)
    new_jobs: List[Tuple[str, Job]] = []
    duplicate_count = 0

    with SeenStore(db_path) as store, httpx.Client(
        headers={"User-Agent": "Mozilla/5.0 (Macintosh) job-watch"}, timeout=20, follow_redirects=True
    ) as client:
        for criteria in config.criteria:
            for source in criteria.sources:
                params = criteria.source_params.get(source, {})
                for keyword in criteria.keywords:
                    log.info("Searching %s for '%s' (%s)...", source, keyword, criteria.label)
                    try:
                        jobs = SOURCES[source](client, keyword, params)
                    except Exception as exc:  # noqa: BLE001 - one broken source shouldn't stop the rest
                        log.error("Search failed on %s for '%s': %s", source, keyword, exc)
                        continue

                    for job in jobs:
                        if not store.is_new(job) or not _passes_filters(job, criteria, cutoff):
                            continue
                        if store.is_duplicate(job):
                            # Same posting already reported from the other site
                            # (or under another keyword) - remember it, don't repeat it.
                            store.mark_seen(job, criteria.label)
                            duplicate_count += 1
                            continue

                        store.mark_seen(job, criteria.label)
                        new_jobs.append((criteria.label, job))
                        print(f"[{criteria.label}] {job.title} - {job.company} ({job.location}) - {job.url}")

                    time.sleep(1.0)  # be polite between requests

    if csv_path and new_jobs:
        _write_csv(csv_path, new_jobs)

    log.info("Done. %d new job(s), %d cross-site duplicate(s) skipped.", len(new_jobs), duplicate_count)
    return len(new_jobs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find new job postings matching your saved criteria.")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config.yaml.")
    parser.add_argument("--db", default="state/job_watch.db", help="Path to the SQLite 'seen jobs' database.")
    parser.add_argument("--csv", default="state/jobs.csv", help="Path to append new jobs to as CSV.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not Path(args.config).exists():
        log.error("Config file not found: %s", args.config)
        sys.exit(1)

    run_once(args.config, args.db, args.csv)


if __name__ == "__main__":
    main()
