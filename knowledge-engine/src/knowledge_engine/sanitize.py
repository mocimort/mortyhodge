"""PII stripping — runs BEFORE storage, enrichment, or any AI sees the data.

Policy (docs/BEFORE-YOU-START.md item 3): keep the technical knowledge,
drop everything that identifies a customer, a person, a price, or an exact
location. Regex catches the structured formats; the enrichment prompt
re-enforces the policy as a second layer.
"""
from __future__ import annotations

import re
from typing import Any

_PATTERNS = [
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "[EMAIL]"),
    (re.compile(r"\$\s?[\d,]+(?:\.\d{2})?"), "[PRICE]"),
    (re.compile(r"\b\d{1,5}\s+\w+(?:\s\w+)?\s(?:st|street|ave|avenue|rd|road|dr|drive|blvd|hwy|highway|pkwy|lane|ln|ct|court|way)\b", re.I), "[ADDRESS]"),
]

# Fields safe to carry through from a ServiceTitan job record
_KEEP_FIELDS = ("id", "jobTypeId", "completedOn", "summary", "businessUnitId")


def scrub_text(text: str) -> str:
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def sanitize_job(job: dict[str, Any], notes: list[dict[str, Any]]) -> dict[str, Any]:
    """Reduce a raw job + notes to an anonymized technical record."""
    return {
        "source_job_id": job.get("id"),
        "completed_on": job.get("completedOn"),
        "summary": scrub_text(str(job.get("summary") or "")),
        "notes": [scrub_text(str(n.get("text") or "")) for n in notes],
    }
