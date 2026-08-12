"""CLI — `python -m knowledge_engine.cli poc --limit 50` runs the proof of concept."""
from __future__ import annotations

import argparse
import sys

from . import db, enrich, sanitize
from .servicetitan import ServiceTitanClient


def run_poc(limit: int) -> None:
    st = ServiceTitanClient()
    conn = db.connect()
    records = []
    print(f"Exporting up to {limit} completed jobs from ServiceTitan...")
    for i, job in enumerate(st.completed_jobs(limit=limit), start=1):
        notes = st.job_notes(job["id"])
        clean = sanitize.sanitize_job(job, notes)
        if not clean["summary"] and not clean["notes"]:
            print(f"  [{i}] job {job['id']}: empty, skipped")
            continue
        try:
            knowledge = enrich.enrich_ticket(clean)
        except Exception as exc:  # keep the POC moving; report at the end
            print(f"  [{i}] job {job['id']}: enrichment failed ({exc})")
            continue
        db.upsert(conn, knowledge)
        records.append(knowledge)
        print(f"  [{i}] job {job['id']}: {knowledge.get('symptom', '?')[:60]}")

    write_report(records)
    print(f"\nDone. {len(records)} knowledge records in data/knowledge.db")
    print("Review poc-report.md, then have a senior tech grade the accuracy.")


def write_report(records: list[dict]) -> None:
    lines = ["# POC Report — ServiceTitan Knowledge Extraction\n"]
    counts = {"high": 0, "medium": 0, "low": 0}
    for k in records:
        counts[k.get("confidence", "low")] = counts.get(k.get("confidence", "low"), 0) + 1
    lines.append(f"Tickets processed: {len(records)}  |  "
                 f"confidence high/med/low: {counts['high']}/{counts['medium']}/{counts['low']}\n")
    for k in records:
        lines += [
            f"## Job {k['source_job_id']} ({k.get('confidence')})",
            f"- **Symptom:** {k.get('symptom')}",
            f"- **Root cause:** {k.get('root_cause')}",
            f"- **Fix:** {k.get('fix')}",
            f"- **Equipment:** {k.get('equipment')}",
            f"- **Tags:** {', '.join(k.get('tags', []))}",
            f"- **Quality note:** {k.get('quality_note')}\n",
        ]
    with open("poc-report.md", "w") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(prog="ke")
    sub = parser.add_subparsers(dest="command", required=True)
    poc = sub.add_parser("poc", help="Run the 25-50 ticket proof of concept")
    poc.add_argument("--limit", type=int, default=50)
    search = sub.add_parser("search", help="Search the knowledge base")
    search.add_argument("query")
    args = parser.parse_args()

    if args.command == "poc":
        run_poc(args.limit)
    elif args.command == "search":
        conn = db.connect()
        for row in db.search(conn, args.query):
            print(f"- [{row['source_job_id']}] {row['symptom']} → {row['root_cause']}")


if __name__ == "__main__":
    sys.exit(main())
