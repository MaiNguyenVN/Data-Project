#!/usr/bin/env python3
"""Download or generate raw legal case data for the project."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_FILE = DATA_DIR / "raw_cases.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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
        "source": "Sample dataset",
        "source_url": "",
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
        "source": "Sample dataset",
        "source_url": "",
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
        "source": "Sample dataset",
        "source_url": "",
    },
]


def rate_limit(calls_per_window: int, window_seconds: int):
    """Simple throttling decorator to reduce API pressure."""

    def decorator(func):
        timestamps: list[float] = []

        def wrapped(*args, **kwargs):
            now = time.monotonic()
            nonlocal timestamps
            timestamps = [stamp for stamp in timestamps if now - stamp < window_seconds]
            if len(timestamps) >= calls_per_window:
                sleep_for = window_seconds - (now - timestamps[0])
                if sleep_for > 0:
                    time.sleep(sleep_for)
                    now = time.monotonic()
                    timestamps = []
            timestamps.append(now)
            return func(*args, **kwargs)

        return wrapped

    return decorator


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def extract_keywords(raw_keywords: Any, case_name: str = "") -> list[str]:
    """Normalise legal keywords and derive a few from the case name when needed."""
    keywords: list[str] = []

    if isinstance(raw_keywords, list):
        for item in raw_keywords:
            keyword = clean_text(item)
            if keyword:
                keywords.append(keyword)
    elif isinstance(raw_keywords, str):
        keywords = [partial.strip() for partial in raw_keywords.split(",") if partial.strip()]

    if not keywords:
        legal_terms = [
            "employment",
            "tribunal",
            "appeal",
            "review",
            "contract",
            "civil",
            "damages",
            "public law",
            "judicial review",
        ]
        case_name_lower = case_name.lower()
        keywords = [term for term in legal_terms if term.lower() in case_name_lower]

    return keywords[:10] or ["legal"]


def _extract_from_nested(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("name", "title", "court_name", "label"):
            nested_value = value.get(key)
            if nested_value:
                return clean_text(nested_value)
        return ""
    if isinstance(value, list):
        return ", ".join(clean_text(item) for item in value if clean_text(item))
    return clean_text(value)


def parse_national_archives_case(raw_case: dict[str, Any]) -> dict[str, Any] | None:
    """Parse National Archives JSON into the project schema."""
    if not isinstance(raw_case, dict):
        return None

    case_name = (
        raw_case.get("case_name")
        or raw_case.get("name")
        or raw_case.get("title")
        or raw_case.get("party_names")
        or "Unknown case"
    )
    neutral_citation = (
        raw_case.get("neutral_citation")
        or raw_case.get("citation")
        or raw_case.get("neutralCitation")
        or ""
    )
    court = _extract_from_nested(raw_case.get("court")) or raw_case.get("court_name") or "Unknown court"
    judge = (
        raw_case.get("judge")
        or raw_case.get("judges")
        or _extract_from_nested(raw_case.get("judge_name"))
        or "Not specified"
    )
    decision_date = (
        raw_case.get("decision_date")
        or raw_case.get("date")
        or raw_case.get("judgment_date")
        or raw_case.get("date_of_judgment")
        or ""
    )
    parties = (
        raw_case.get("parties")
        or raw_case.get("party_names")
        or raw_case.get("name")
        or case_name
    )
    content = (
        raw_case.get("content")
        or raw_case.get("summary")
        or raw_case.get("text")
        or "No summary available."
    )
    source_url = raw_case.get("source_url") or raw_case.get("url") or ""

    return {
        "case_name": clean_text(case_name),
        "neutral_citation": clean_text(neutral_citation),
        "judge": clean_text(judge),
        "court": clean_text(court),
        "decision_date": clean_text(decision_date),
        "parties": clean_text(parties),
        "keywords": extract_keywords(raw_case.get("keywords"), clean_text(case_name)),
        "content": clean_text(content),
        "source": "National Archives",
        "source_url": clean_text(source_url),
    }


@rate_limit(calls_per_window=8, window_seconds=60)
def fetch_national_archives_caselaw() -> list[dict[str, Any]]:
    """Fetch data from the National Archives Find Case Law API."""
    queries = [
        "employment",
        "judicial review",
        "contract",
        "appeal",
        "civil",
    ]
    combined: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for query in queries:
        search_url = (
            "https://api.caselaw.nationalarchives.gov.uk/search/"
            f"?q={query.replace(' ', '+')}&page_size=20"
        )
        try:
            request = Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            logger.warning("Could not fetch query '%s': %s", query, exc)
            continue

        results = payload.get("results", []) if isinstance(payload, dict) else payload
        if not isinstance(results, list):
            continue

        for item in results:
            parsed = parse_national_archives_case(item)
            if not parsed:
                continue
            key = parsed.get("neutral_citation") or parsed.get("case_name")
            if key and key not in seen_ids:
                seen_ids.add(key)
                combined.append(parsed)

    return combined


def fetch_live_data() -> list[dict[str, Any]]:
    """Prefer live public legal data, but fall back to local sample data when necessary."""
    live_cases = fetch_national_archives_caselaw()
    if live_cases:
        logger.info("Fetched %s live case records from the National Archives API.", len(live_cases))
        return live_cases

    logger.warning("No live data could be fetched; falling back to the sample dataset.")
    return [dict(case) for case in SAMPLE_CASES]


def write_raw_cases(cases: list[dict[str, Any]]) -> None:
    """Write cleaned, deduplicated data to the raw JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    deduplicated: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    for case in cases:
        if not isinstance(case, dict):
            continue
        case_name = clean_text(case.get("case_name") or case.get("name") or "")
        citation = clean_text(case.get("neutral_citation") or case.get("citation") or "")
        key = citation or case_name
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)

        normalized = {
            "case_name": case_name or "Unknown case",
            "neutral_citation": citation or "Unknown citation",
            "judge": clean_text(case.get("judge") or "Not specified"),
            "court": clean_text(case.get("court") or "Unknown court"),
            "decision_date": clean_text(case.get("decision_date") or ""),
            "parties": clean_text(case.get("parties") or case_name or "Unknown parties"),
            "keywords": extract_keywords(case.get("keywords"), case_name),
            "content": clean_text(case.get("content") or "No summary available."),
            "source": clean_text(case.get("source") or "Sample dataset"),
            "source_url": clean_text(case.get("source_url") or ""),
        }
        deduplicated.append(normalized)

    RAW_FILE.write_text(json.dumps(deduplicated, indent=2), encoding="utf-8")
    logger.info("Saved %s case records to %s", len(deduplicated), RAW_FILE)


def main() -> None:
    cases = fetch_live_data()
    write_raw_cases(cases)


if __name__ == "__main__":
    main()
