"""Danish date lines for invitations. Weekdays are computed, never typed, because
a wrong weekday on an invitation is the classic mistake."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple

WEEKDAYS = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli",
          "august", "september", "oktober", "november", "december"]


def parse(value: Any) -> Tuple[datetime, bool]:
    """'2026-11-07' or '2026-11-07 10:00' -> (datetime, has_time)."""
    if isinstance(value, datetime):
        return value, True
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day), False
    text = str(value).strip()
    return datetime.fromisoformat(text), len(text) > 10


def _day(d: datetime, year: bool = False) -> str:
    return f"{d.day}. {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def _time(d: datetime) -> str:
    return f"{d.hour:02d}.{d.minute:02d}"


def _kl(d: datetime) -> str:
    # Non-breaking space, so a line never ends on a bare "kl.".
    return f"kl.\u00a0{_time(d)}"


def long_date(value: Any) -> str:
    """'søndag 1. november'. Text that isn't a date (e.g. 'snarest') passes through."""
    try:
        d, _ = parse(value)
    except ValueError:
        return str(value)
    return f"{WEEKDAYS[d.weekday()]} {_day(d)}"


def when(starts: Any, ends: Optional[Any] = None) -> Dict[str, Optional[str]]:
    """Two lines: `day` (big) and `time` (small, may be None)."""
    s, s_time = parse(starts)
    if ends is None:
        return {"day": long_date(starts).capitalize(), "time": _kl(s) if s_time else None}
    e, e_time = parse(ends)
    if e < s:
        raise ValueError(f"ends ({ends}) is before starts ({starts})")
    if s.date() == e.date():
        time = f"{_kl(s)}–{_time(e)}" if s_time and e_time else (_kl(s) if s_time else None)
        return {"day": long_date(starts).capitalize(), "time": time}

    if s.year != e.year:
        day = f"{_day(s, year=True)} – {_day(e, year=True)}"
    elif s.month != e.month:
        day = f"{_day(s)} – {_day(e)}"
    else:
        day = f"{s.day}.–{_day(e)}"
    start = WEEKDAYS[s.weekday()] + (f"\u00a0{_kl(s)}" if s_time else "")
    end = WEEKDAYS[e.weekday()] + (f"\u00a0{_kl(e)}" if e_time else "")
    sep = " – " if s_time or e_time else "–"
    return {"day": day, "time": f"{start}{sep}{end}".capitalize()}
