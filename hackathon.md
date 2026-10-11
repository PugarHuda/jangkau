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
- Done: LiteLLM key claimed. First real run on `index.html` (claude-sonnet-4.6): 25 → 0 nodes.
  A real recovery happened: the first `select-name` fix added 6 `region` violations, was rejected and rolled back, then fixed on attempt 2.
  However, v1 (`--no-verify`) also reached 0, so the page was too easy to show improvement.
- Done: added a harder page `demo_site/toko.html` (batik shop): 47 failing nodes across 14 rules.
  Real images added to the demo (missing images made Chrome collapse the cards).
- Iteration, all on claude-haiku with toko.html (local run data in `runs/dbg-toko-*`, not exported to neatlogs yet):

  | Version | Change | Nodes left | LLM calls | Tokens in/out | Time |
  |---|---|---|---|---|---|
  | v1 | no verification | 10 | 14 | 28.4k / 3.9k | 61s |
  | v2 | verify + revert | 13 (worse) | 18 | 35.9k / 5.3k | 78s |
  | v3 | allow growth in still-queued rules; keep partial progress and retry the rest | 1 | 18 | 36.9k / 5.3k | 81s |
  | v4 | rejection feedback includes the broken node + axe failure summary | **0** | 16 | 33.1k / 5.1k | 71s |

  Root causes found from run logs: (a) v2 rejected a correct `<label>` fix because it added `region`
  nodes, a rule still waiting in the queue; (b) `color-contrast` 18 → 9 was marked fixed and the 9 left were never retried;
  (c) `page-has-heading-one` failed 3 times because the feedback only gave the rule name, not the broken heading.
- Total LiteLLM spend so far: about $0.46 of $20.
- Pending: NEATLOGS_API_KEY, then re-run v1 → v4 with traces exported for shareable before/after evidence.

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
