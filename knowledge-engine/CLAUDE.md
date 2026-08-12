# Hodge Knowledge Engine — notes for Claude Code

- This is Morty's ServiceTitan → knowledge base → content pipeline. Read
  `README.md` for architecture and `docs/BEFORE-YOU-START.md` for status.
- **Never** commit `.env`, anything under `data/`, `raw/`, `exports/`, or
  `poc-report.md` — they contain credentials or customer-derived data.
- PII policy is enforced in `src/knowledge_engine/sanitize.py` and re-stated
  in the enrichment prompt. Any new data path must go through `sanitize`
  before storage or any model call.
- Target machine is morty-mini (Mac mini M4 Pro, always-on). Scheduled runs
  belong in launchd plists, not cron.
- Style: plain Python, stdlib-first, one obvious way to do things — this
  must stay maintainable by a non-developer with AI help.
