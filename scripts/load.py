#!/usr/bin/env python3
"""Clean and load the raw case records into SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw_cases.json"
DB_PATH = BASE_DIR / "database" / "cases.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def normalize_case(raw_case: dict[str, Any]) -> dict[str, Any]:
    case_name = raw_case.get("case_name") or raw_case.get("name") or "Unknown case"
    neutral_citation = raw_case.get("neutral_citation") or raw_case.get("citation") or "Unknown citation"
    judge = raw_case.get("judge") or raw_case.get("judges") or "Unknown judge"
    court = raw_case.get("court") or raw_case.get("court_name") or "Unknown court"
    decision_date = raw_case.get("decision_date") or raw_case.get("date") or "1970-01-01"
    parties = raw_case.get("parties") or raw_case.get("party_names") or case_name
    keywords = raw_case.get("keywords") or []
    content = raw_case.get("content") or raw_case.get("summary") or "No summary available."

    if isinstance(keywords, str):
        keywords = [keyword.strip() for keyword in keywords.split(",") if keyword.strip()]

    return {
        "case_name": case_name,
        "neutral_citation": neutral_citation,
        "judge": judge,
        "court": court,
        "decision_date": decision_date,
        "parties": parties,
        "keywords": ", ".join(keywords),
        "content": content,
    }


def transform_cases() -> list[dict[str, Any]]:
    raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    normalized = [normalize_case(item) for item in raw if isinstance(item, dict)]

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    conn.executemany(
        """
        INSERT OR REPLACE INTO cases 
        (case_name, neutral_citation, judge, court, decision_date, parties, keywords, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["case_name"],
                row["neutral_citation"],
                row["judge"],
                row["court"],
                row["decision_date"],
                row["parties"],
                row["keywords"],
                row["content"],
            )
            for row in normalized
        ],
    )
    conn.commit()
    conn.close()

    print(f"Loaded {len(normalized)} normalized records into {DB_PATH}")
    return normalized


def main() -> None:
    transform_cases()


if __name__ == "__main__":
    main()
