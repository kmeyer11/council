"""SQLite-backed 'seen items' store so runs only report new matches."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Union

from .dedupe import normalize_title


class SeenStore:
    def __init__(self, db_path: Union[str, Path] = "vinted_watch.db"):
        self.db_path = Path(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_items (
                item_id TEXT PRIMARY KEY,
                watch_name TEXT NOT NULL,
                title TEXT,
                price TEXT,
                url TEXT,
                first_seen TEXT NOT NULL
            )
            """
        )
        self._migrate_normalized_title_column()
        self._conn.commit()

    def _migrate_normalized_title_column(self) -> None:
        cols = {row[1] for row in self._conn.execute("PRAGMA table_info(seen_items)")}
        if "normalized_title" not in cols:
            self._conn.execute("ALTER TABLE seen_items ADD COLUMN normalized_title TEXT")
            for item_id, title in self._conn.execute("SELECT item_id, title FROM seen_items"):
                self._conn.execute(
                    "UPDATE seen_items SET normalized_title = ? WHERE item_id = ?",
                    (normalize_title(title or ""), item_id),
                )

    def is_new(self, item_id: str) -> bool:
        cur = self._conn.execute("SELECT 1 FROM seen_items WHERE item_id = ?", (item_id,))
        return cur.fetchone() is None

    def all_normalized_titles(self) -> List[str]:
        cur = self._conn.execute(
            "SELECT normalized_title FROM seen_items WHERE normalized_title IS NOT NULL AND normalized_title != ''"
        )
        return [row[0] for row in cur.fetchall()]

    def mark_seen(self, item_id: str, watch_name: str, title: str, price: str, url: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO seen_items "
            "(item_id, watch_name, title, price, url, first_seen, normalized_title) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                item_id,
                watch_name,
                title,
                price,
                url,
                datetime.now(timezone.utc).isoformat(),
                normalize_title(title or ""),
            ),
        )
        self._conn.commit()

    def forget(self, item_id: str) -> None:
        """Un-mark an item as seen, so a future watch run treats it as new
        again if it turns up in search results (e.g. after deliberately
        unfavouriting it, in case you want to reconsider it later)."""
        self._conn.execute("DELETE FROM seen_items WHERE item_id = ?", (item_id,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "SeenStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
