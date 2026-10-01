"""Jobnet.dk via the JSON endpoint its own search page calls.

Not a documented public API - it's what jobnet.dk/find-job fetches in the
browser. The `x-csrf: 1` header is required (the site's fetch wrapper always
sends it; without it the endpoint answers 401). If this breaks, open
jobnet.dk/find-job with DevTools -> Network and compare the request.
Extra params (e.g. `regions: HovedstadenOgBornholm`, `postalCode`,
`kmRadius`) go in a criteria file's `jobnet:` block.
"""
from __future__ import annotations

import html
from datetime import datetime
from typing import Any, Dict, List

import httpx

from ..models import Job

SEARCH_URL = "https://jobnet.dk/bff/FindJob/Search"
AD_URL = "https://jobnet.dk/find-job/{id}"


def search(client: httpx.Client, keyword: str, params: Dict[str, Any]) -> List[Job]:
    query = {
        "searchString": keyword,
        "orderType": "PublicationDate",
        "resultsPerPage": 50,
        "pageNumber": 1,
        **params,
    }
    resp = client.get(SEARCH_URL, params=query, headers={"x-csrf": "1", "Accept": "application/json"})
    resp.raise_for_status()

    jobs: List[Job] = []
    for ad in resp.json().get("jobAds", []):
        pub = ad.get("publicationDate")
        location = ", ".join(
            str(p) for p in (ad.get("postalDistrictName"), ad.get("municipality")) if p
        )
        jobs.append(
            Job(
                source="jobnet",
                id=ad["jobAdId"],
                title=html.unescape(ad.get("title") or "").strip(),
                company=html.unescape(ad.get("hiringOrgName") or "").strip(),
                location=location,
                # External ads (copied in from other sites) carry their own URL.
                url=ad.get("jobAdUrl") or AD_URL.format(id=ad["jobAdId"]),
                published=datetime.fromisoformat(pub) if pub else None,
            )
        )
    return jobs
