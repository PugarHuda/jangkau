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
- Done: neatlogs connected (SDK Doctor `--probe`: PASS). `scripts/evidence.sh` re-ran v1 / v2 (commit 963a4dd) / v4
  with export on and the same results: v1 10 left, v2 14 left, v4 0 left. Runs now record their neatlogs trace ID
  (taken from `inject_trace_context`): v1 `002efc98d1c3610e269f95108e5371d4`, v4 `8ad9968fc9a602e0dad474b24842835f`.
- Done: landing page live at https://jangkau-jet.vercel.app (axe: 0 violations after the hero fix animation).

### 2026-10-12
- Done: `--pr` mode. Writes the fixed page back into its git repo on a new branch, pushes, and opens a PR
  with `report.md` as the description. Real run on `demo_site/index.html`: 25 → 0, https://github.com/PugarHuda/jangkau/pull/1
- Done: first run on a real third-party page, StartBootstrap Freelancer `dist/index.html` (unmodified): 33 failing nodes, 5 rules.
  v4 got it to 4. Four root causes found and fixed (v5), one per rerun:
  1. Every correct contrast fix was rejected as "35% of pixels changed". Darkening a brand-colour section
     repaints most of the page. Fix: contrast fixes compare edge maps (layout), not raw pixels → 33 → 1.
  2. Retries on the last node got "still has 1 failing nodes" and nothing else. Fix: feedback includes the
     contrast axe measured on the rendered page after the edit. The model went 2.73 → 3.44 but Haiku stalled there.
  3. Fix: the last attempt on a stuck rule escalates to claude-sonnet-4.6. It found Bootstrap's
     `.disabled { opacity: .65 }` → 33 → 0.
  4. Inspecting the diff showed `landmark-one-main` was "fixed" with an empty `<main></main>`. axe passes it, but the content
     wasn't wrapped. Fix: the verifier rejects any edit that adds an empty landmark. Rerun: `<main>` now wraps the page, 33 → 0, 7 LLM calls, 40 s.
  Regression check on toko.html with v5: still 47 → 0 (trace `7ebe2d0264836eb6ec3fa6d932feafdb`).
- Done: Entire checkpoints are recorded. Sessions now start inside jangkau/, so the Claude Code hooks fire (the earlier session ran from the parent folder, where the hooks never loaded).
- Pending: confirm the traces in the dashboard and add share links; Entire checkpoint link + ID; cfo.ai model; tweets; demo video.

## Demo
Pending.

## Known limitations and next steps
- One HTML file per run (no multi-page crawl yet).
- `--pr` handles one page per PR and needs `gh` logged in with push access to the repo.
- Fixes land as an inline `<style>` override in the page, not in the source stylesheet or the build (Sass/templates).

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
