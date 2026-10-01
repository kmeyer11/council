"""Jobindex.dk via its public RSS feed (same query params as the search page,
so anything filterable on the site - e.g. `geoareaid` - can be copied from a
jobindex.dk search URL into a criteria file's `jobindex:` block)."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List

import httpx

from ..models import Job

RSS_URL = "https://www.jobindex.dk/jobsoegning.rss"
_AREA_RE = re.compile(r'class="jix_robotjob--area">([^<]+)<')
_H4_RE = re.compile(r"<h4>(.*?)</h4>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_ID_RE = re.compile(r"/(\d+)$")


def search(client: httpx.Client, keyword: str, params: Dict[str, Any]) -> List[Job]:
    resp = client.get(RSS_URL, params={"q": keyword, "sort": "date", **params})
    resp.raise_for_status()
    # Feed is ISO-8859-1; parse bytes so ElementTree honours the XML declaration.
    root = ET.fromstring(resp.content)

    jobs: List[Job] = []
    for item in root.iter("item"):
        description = html.unescape(item.findtext("description") or "")
        full_title = (item.findtext("title") or "").strip()
        # Feed title is "{job title}, {company}" and both halves can contain
        # commas, so take the job title from the ad's <h4> and treat the rest
        # as the company.
        h4 = _H4_RE.search(description)
        title = html.unescape(_TAG_RE.sub("", h4.group(1))).strip() if h4 else ""
        if title and full_title.startswith(title + ", "):
            company = full_title[len(title) + 2 :]
        else:
            title, company = full_title, ""

        guid = item.findtext("guid") or ""
        m = _ID_RE.search(guid)
        job_id = m.group(1) if m else guid

        areas = [a.strip() for a in _AREA_RE.findall(description)]

        pub = item.findtext("pubDate")
        jobs.append(
            Job(
                source="jobindex",
                id=job_id,
                title=title.strip(),
                company=company.strip(),
                location=", ".join(areas),
                url=(item.findtext("link") or "").strip(),
                published=parsedate_to_datetime(pub) if pub else None,
            )
        )
    return jobs
