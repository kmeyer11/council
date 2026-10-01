from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Team:
    id: int
    name: str
    logo_url: str
    score: int


@dataclass
class Event:
    minute: str
    player: str
    side: str  # "home" | "away" - the side the event counts for
    note: str = ""  # "pen" | "og" | "" for goals, "" for cards


@dataclass
class Match:
    fixture_id: int
    date: str  # yyyy-mm-dd, local kickoff date
    competition: str
    round: str
    venue: str
    home: Team
    away: Team
    goals: List[Event] = field(default_factory=list)
    red_cards: List[Event] = field(default_factory=list)
    penalties: Optional[str] = None  # "4-3" after a shootout


@dataclass
class FixtureSummary:
    """One line in the "is this the right match?" pick list."""
    id: int
    date: str
    competition: str
    home_id: int
    home: str
    away_id: int
    away: str
    home_score: int
    away_score: int
