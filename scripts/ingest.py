#!/usr/bin/env python3
"""Download or generate raw legal case data for the project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_FILE = DATA_DIR / "raw_cases.json"

SAMPLE_CASES: list[dict[str, Any]] = [
    {
        "case_name": "R v Smith",
        "neutral_citation": "[2025] EWHC 1201",
        "judge": "Mr Justice Smith",
        "court": "High Court",
        "decision_date": "2025-06-12",
        "parties": "R v Smith",
        "keywords": ["civil", "contract", "damages"],
        "content": "The claimant sought damages for breach of contract after the defendant failed to deliver goods on time. The court considered the evidence and awarded partial damages.",
    },
    {
        "case_name": "Jones v Employment Tribunal Appeal Board",
        "neutral_citation": "[2026] EAT 87",
        "judge": "Judge Mellor",
        "court": "Employment Appeal Tribunal",
        "decision_date": "2026-01-21",
        "parties": "Jones v Employment Tribunal Appeal Board",
        "keywords": ["employment", "tribunal", "unfair dismissal"],
        "content": "The appellant challenged the decision of the industrial tribunal. The court held that the tribunal had erred in applying the legal test and remitted the matter for rehearing.",
    },
    {
        "case_name": "Acme Ltd v Local Authority",
        "neutral_citation": "[2025] EWCA Civ 455",
        "judge": "Lady Justice Patel",
        "court": "Court of Appeal",
        "decision_date": "2025-09-03",
        "parties": "Acme Ltd v Local Authority",
        "keywords": ["appeal", "public law", "judicial review"],
        "content": "The appeal concerned the lawfulness of a local authority decision under the planning regime. The Court of Appeal found that the decision was materially flawed and quashed it.",
    },
]


def fetch_live_data() -> list[dict[str, Any]]:
    """Try to fetch live public legal data. If the API is unavailable, return the sample data."""
    urls = [
        "https://api.caselaw.nationalarchives.gov.uk/search/?q=employment+tribunal",
        "https://api.caselaw.nationalarchives.gov.uk/search/?q=judicial+review",
    ]

    for url in urls:
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))

            results = payload.get("results") if isinstance(payload, dict) else payload
            if isinstance(results, list) and results:
                return results
        except (HTTPError, URLError, TimeoutError, ValueError):
            continue

    return SAMPLE_CASES


def write_raw_cases(cases: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_FILE.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Saved {len(cases)} case records to {RAW_FILE}")


def main() -> None:
    cases = fetch_live_data()
    write_raw_cases(cases)


if __name__ == "__main__":
    main()
