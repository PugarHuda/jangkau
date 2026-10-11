# neatHack build log

## Project
**Jangkau** is an agent that makes a web page meet WCAG and proves every fix.
Problem: most small-business sites fail basic accessibility checks. Audit tools
only list the issues, and manual remediation costs $1,000–5,000 per site.

## Team
Ampun (Pugar Huda Mantoro)

## Stack
- Python 3.12, Playwright (Chromium), axe-core via `axe-playwright-python`, Pillow
- LLM: neatHack LiteLLM proxy (`claude-sonnet-4.6` by default)
- neatlogs: `neatlogs` Python SDK (OpenAI auto-instrumentation plus WORKFLOW/AGENT/TOOL spans)
- Entire: CLI 0.11.4, `entire enable --agent claude-code`
- cfo.ai: business model (pending), inputs in `BUSINESS.md`

## Build log

### 2026-10-11
- Done: researched about 60 public neatHack repos to avoid crowded ideas
  (self-healing agents, coding-agent supervisors, OSINT research). Picked WCAG remediation.
- Done: built the agent loop: audit → fix per rule (most severe first) → verify
  (rule nodes down, no new violations, no content removed, visual diff ≤ 35%) →
  revert and retry with the reason (max 3) → checkpoint `state.json` → `report.md`.
- Done: `demo_site/index.html` audited for real with axe-core: **25 failing nodes across 10 rules**.
- Done: tests run, `pytest`: 3 passed (edit application, ambiguous-match rejection, JSON parsing).
- Done: smoke run with a scripted fake LLM (not a real model). It exercised these paths:
  bad JSON → retry → fixed; non-unique `find` → retry; an edit that deleted an image
  was caught by the content guard and reverted. Real-model runs are still pending.
- Done: Entire enabled. Repo is public at https://github.com/PugarHuda/jangkau
- Pending: claim the LiteLLM key, run v1 (`--no-verify`) and v2, then compare traces in neatlogs.

## Demo
Pending.

## Known limitations and next steps
- One HTML file per run (no multi-page crawl yet).
- The visual diff threshold is global. Color-contrast fixes may need a looser limit.
- No PR creation yet. Output is the patched file plus `report.md`.

## Submission
Confirmed requirements (from https://neatlogs.com/hackathon and the organiser email):
- [ ] Quote tweet of the official neatlogs post: team, name, project, public repo, demo
      (Mon 12 Oct, 7:00–11:55 PM IST; final cutoff on Discord)
- [ ] neatlogs trace links/screenshots, plus before/after runs with the numbers
- [ ] Entire checkpoint link + checkpoint ID (`https://entire.io/gh/PugarHuda/jangkau/commit/<sha>`)
- [ ] cfo.ai business plan (pricing, costs, revenue, runway)
- [ ] A run showing failure and recovery
- [ ] #neatHack build-in-public posts
- [x] Public repo with commits dated during the hackathon
