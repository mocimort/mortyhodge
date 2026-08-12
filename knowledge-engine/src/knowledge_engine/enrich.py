"""Enrichment — Claude turns an anonymized ticket into structured knowledge.

One ticket in, one JSON knowledge record out: symptom, root cause, fix,
equipment, tags. This is the step that converts "service history" into
"knowledge base".
"""
from __future__ import annotations

import json
from typing import Any

import anthropic

from .config import settings

MODEL = "claude-sonnet-5"  # fast + cheap enough to run over thousands of tickets

SYSTEM = """You extract structured service knowledge from anonymized industrial
air-compressor service tickets for Hodge Compressor.

Return ONLY a JSON object with these keys:
  symptom        - what the customer reported / what was observed
  root_cause     - the actual diagnosed cause ("unknown" if not determinable)
  fix            - what resolved it, step by step if the notes support it
  equipment      - make/model/type/HP if mentioned, else "unspecified"
  parts_used     - list of parts, [] if none mentioned
  industry       - customer's industry if inferable (e.g. "poultry processing"), else null
  tags           - 3-8 lowercase topical tags (e.g. "rotary-screw", "overheating")
  confidence     - "high" | "medium" | "low": how complete the ticket was
  quality_note   - one sentence on what's missing or unclear, if anything

Never include customer names, people's names, addresses, phone numbers,
emails, or prices — if any slipped through sanitization, omit them."""


def enrich_ticket(record: dict[str, Any]) -> dict[str, Any]:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    ticket_text = record["summary"] + "\n\nNOTES:\n" + "\n---\n".join(record["notes"])
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": ticket_text[:12000]}],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    knowledge = json.loads(raw)
    knowledge["source_job_id"] = record["source_job_id"]
    knowledge["completed_on"] = record["completed_on"]
    return knowledge
