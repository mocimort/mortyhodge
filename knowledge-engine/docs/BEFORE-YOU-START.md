# Before You Start — Pre-Flight Checklist

Work through these in order. Items 1–3 are blockers; the rest can happen in
parallel with the proof of concept.

## 1. Move this to a private repo ⛔ BLOCKER

This starter kit currently lives in the **public** mortyhodge.com website
repo. Customer service history is a competitive asset (that's the whole
point) and must never be public.

- Create `hodge-knowledge-engine` as a **private** repo under your GitHub
  account (or the company org if you want the team contributing).
- Move this `knowledge-engine/` folder there; delete it from the website repo.
- Claude Code can do both steps for you — just ask.

## 2. Verify ServiceTitan API scopes ⛔ BLOCKER

You have credentials, but the June membership-estimate project proved they
had **read-only, limited scopes** (customer creation was rejected for missing
write scope). This project only needs READ, but confirm the app has read
access to the right modules:

- **JPM (Job Planning & Management):** jobs, job notes, appointments
- **CRM:** customers, locations (needed to know equipment context — gets
  anonymized immediately)
- **Accounting/Invoices:** invoice line items often contain the best
  "what we actually did" descriptions
- **Equipment systems:** installed equipment records (make/model/serial)

Check in ServiceTitan: Settings → Integrations → API Application Access.
If scopes are missing, whoever admins the developer portal adds them there —
no new app needed.

Credentials you need in `.env`: Client ID, Client Secret, App Key (from the
developer portal), and Tenant ID.

## 3. Decide the PII policy ⛔ BLOCKER

Tickets contain customer names, addresses, phone numbers, and prices. Rule
this codebase enforces: **PII is stripped in step 2 (sanitize) before
anything is stored, enriched, or shown to any AI.** What survives:

- ✅ Equipment make/model/HP, symptom, diagnosis, fix, parts used, industry
  (e.g. "a poultry plant in north Georgia")
- ❌ Customer name, contact info, exact address, pricing, tech names

Decide now: is industry + rough region OK in published content? (Recommended:
yes — it's what makes case studies credible.) Anything customer-identifiable
in a *published* case study needs that customer's sign-off.

## 4. Anthropic API key

Enrichment (turning raw tickets into structured symptom/cause/fix records)
uses the Claude API. Create a key at console.anthropic.com if you don't have
one, and set a monthly spend limit ($50 is plenty for the POC).

## 5. morty-mini readiness

Already done from previous work: always-on, auto-login, restart-on-power,
Tailscale, Claude Code Remote Control. Two open items from your May notes
worth closing before this becomes production:

- **Time Machine to an external SSD** — flagged then as the biggest gap;
  this database becomes exactly the kind of thing you can't lose.
- **Cloudflare Tunnel / hodgeindustrial.ai** — only needed if the MCP server
  should be reachable off-Tailscale (e.g. team ChatGPT connectors). Not
  needed for the POC.

## 6. Delegation (from your Aug 11 post)

You asked for a volunteer to figure out mass-export + write the SOP. With
API access, the export SOP becomes "run this command" — but a human should
still own **quality review**: reading the POC report and grading whether the
extracted knowledge is actually right. A senior service tech is the right
reviewer, not a marketer.

## The order of operations

1. Private repo (item 1)
2. Fill in `.env` (items 2 + 4)
3. `python -m knowledge_engine.cli poc --limit 50`
4. Tech reviews `poc-report.md` for accuracy
5. Green light → scale export to full history, schedule nightly sync via
   launchd on morty-mini, stand up the MCP server, start the content mill
