# Hodge Knowledge Engine

Turn thousands of real ServiceTitan service tickets into the most valuable
compressed-air service knowledge library on the internet — and a universal
database any AI (Claude, ChatGPT, Gemini, or future Hodge projects) can plug
into.

> **⚠️ This folder is a STARTER KIT living temporarily in the public
> mortyhodge.com website repo.** Before any real credentials or customer data
> touch this code, move it to a **private** repo (e.g.
> `mocimort/hodge-knowledge-engine`). Never commit `.env`, exported tickets,
> or the database file — `.gitignore` here already blocks them.

## Where this runs

**morty-mini** (Mac mini M4 Pro, 64GB, always-on, Tailscale, Claude Code
Remote Control) — your existing always-on workstation. This follows the same
local-first principle as your Second Brain: proprietary knowledge lives on
your machine, not inside someone else's chat platform.

## Architecture

```
ServiceTitan API ──▶ 1. EXTRACT ──▶ 2. SANITIZE ──▶ 3. ENRICH ──▶ 4. STORE
  (jobs, notes,       raw JSON        strip PII        Claude API     SQLite +
   invoices)          on disk         (names, $,       tags each      full-text
                                      addresses)       ticket:        search
                                                       symptom /
                                                       cause / fix
                                                            │
              ┌─────────────────────────────────────────────┘
              ▼
        5. SERVE (MCP server)                6. GENERATE (content)
        Universal connector:                 Case studies, FAQs, blogs,
        Claude, ChatGPT, Gemini,             training material, video
        and any future project               scripts, llms.txt / AEO
        all speak MCP today                  content for mortyhodge.com
                                             and hodge sites
```

**Why SQLite + MCP (and not a cloud vector DB):**

- One file, zero servers to babysit, Time Machine backs it up — same
  "simple enough to maintain solo" principle as the Container Planner.
- MCP (Model Context Protocol) is the one connector Claude, ChatGPT, and
  Gemini all support. Build the server once, every AI platform and every
  future Hodge project connects to the same brain.
- SQLite FTS5 gives instant keyword search; embeddings can be added later
  without changing anything upstream.

## Layout

| Path | What it is |
|---|---|
| `docs/BEFORE-YOU-START.md` | The pre-flight checklist — do this first |
| `src/knowledge_engine/servicetitan.py` | ServiceTitan API client (auth + export) |
| `src/knowledge_engine/sanitize.py` | PII stripping before anything else sees the data |
| `src/knowledge_engine/enrich.py` | Claude turns raw tickets into structured knowledge |
| `src/knowledge_engine/db.py` | SQLite schema + search |
| `src/knowledge_engine/cli.py` | `poc` command — the 25–50 ticket proof of concept |
| `mcp_server/server.py` | MCP server exposing the knowledge base to any AI |
| `.env.example` | Every secret the system needs (copy to `.env`, never commit) |

## The proof of concept (first milestone)

Exactly what you called for in #leadership_team: pull 25–50 tickets, run the
pipeline end to end, and judge the output quality before scaling to
thousands.

```bash
cd knowledge-engine
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env   # fill in ServiceTitan + Anthropic credentials
python -m knowledge_engine.cli poc --limit 50
```

Output: `data/knowledge.db` plus a `poc-report.md` showing each ticket's
extracted symptom → cause → fix, so you can eyeball whether the knowledge is
good enough to build on.
