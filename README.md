# Jangkau

> *jangkau* (Indonesian): to reach. A web page should reach everyone.

**Jangkau is an agent that makes a web page accessible, and proves every fix.** · [Live demo](https://jangkau-jet.vercel.app)
It audits the page against WCAG with axe-core, fixes one violation at a time,
and only keeps a fix when three independent checks pass. Otherwise it rolls the
edit back and tries again with the reason it failed.

About 1 in 6 people live with a disability, and the European Accessibility Act has
been enforceable since June 2025. Most small sites still fail basic checks.
Audit tools only list the problems. Jangkau fixes them.

Built during [#neatHack](https://neatlogs.com/hackathon), Oct 10–12 2026.

## How it works

```
audit (axe-core + screenshot + content fingerprint)
  └─ for each violation, most severe first
       ├─ LLM proposes find/replace edits
       ├─ apply  ── find not unique / bad JSON? ──► retry with the error
       ├─ re-audit + verify:
       │    1. the rule's failing nodes went down
       │    2. no new violations appeared
       │    3. no content was deleted (elements + text length)
       │    4. no empty landmark was added (an empty <main> games axe)
       │    5. the page still looks the same (pixel diff ≤ 35%; edge diff
       │       for contrast fixes, so a recolour passes but a moved layout fails)
       ├─ any check fails ──► revert, retry with the measured failure (max 3,
       │                       the last attempt escalates to a stronger model)
       └─ checkpoint state.json (an interrupted run resumes)
final audit ──► report.md (before/after, tokens, time)
--pr ──► branch + commit the fixed page in its repo, open a PR with the report
```

The content guard matters. The cheapest way for an LLM to "fix" a missing alt
attribute is to delete the image. Jangkau catches that and reverts it.

| Focus area | In Jangkau |
|---|---|
| Planning | Violations ordered by impact (critical → minor) |
| Tool use | axe-core audit, file edits, screenshot diff |
| State | `state.json` after every rule. Re-run with the same `--out` to resume |
| Recovery | Revert and retry with the concrete failure reason |
| Verification | Re-audit, content guard, visual diff |
| Iteration | Each failed attempt's reason goes into the next prompt |

## Run it

```bash
uv venv && uv pip install -r requirements.txt
.venv/Scripts/python -m playwright install chromium   # macOS/Linux: .venv/bin/python
cp .env.example .env    # LITELLM_API_KEY from neatlogs.com/hackathon/models + NEATLOGS_API_KEY

python jangkau.py demo_site/index.html                  # verified agent (v2)
JANGKAU_VERSION=v1 python jangkau.py demo_site/index.html --no-verify   # baseline, no checks
python jangkau.py path/to/your/repo/index.html --pr    # fix a page in a git repo and open a PR (needs gh)
python -m pytest -q
```

`demo_site/` is a small coffee shop page with 25 failing nodes across 10 WCAG rules.

## Evidence for judges

| Claim | Evidence |
|---|---|
| The agent improved | Same page (`demo_site/toko.html`, 47 failing nodes), same model (claude-haiku), traced in neatlogs and filtered by tag `version:v1` / `version:v2` / `version:v4`. **v1** (no checks): 10 left, 14 LLM calls. **v2** (first verifier): 14 left, 18 calls. **v4**: **0 left**, 16 calls. Reports in `runs/ev-*/report.md`. Root causes are in [hackathon.md](hackathon.md) |
| We used neatlogs | Each run is a `jangkau_run` workflow trace with `fix_rule` agent spans, `audit` / `apply_edits` / `visual_diff` tool spans and auto-captured LLM calls. Trace IDs: v1 `002efc98d1c3610e269f95108e5371d4`, v4 `8ad9968fc9a602e0dad474b24842835f`. SDK Doctor probe: PASS |
| We used Entire | [Entire Graph impact + diff](docs/entire-graph.md) for the verifier changes. Checkpoints (stored as git refs): checkpoint `01M4PZ7CYXWQQTTBCQ1QKJ075N` on commit [9713fcd](https://entire.io/gh/PugarHuda/jangkau/commit/9713fcd8e88c8a88519e718dc8e8ac2c7ea883f8); every agent session in `jangkau/` is recorded from Oct 12 |
| We used cfo.ai | [BUSINESS.md](BUSINESS.md) + the cfo.ai model. _TODO: link/screenshot_ |
| It works on real pages | [StartBootstrap Freelancer](https://github.com/StartBootstrap/startbootstrap-freelancer) (`dist/index.html`, unmodified): **33 → 0** failing nodes, 7 LLM calls, 40 s. Layout unchanged, brand teal darkened to pass contrast. Run in `runs/real-freelancer/` (`compare.png` before/after), trace `28e57df2617c4345e0f2679a1b99ed94` |
| It opens real PRs | `--pr` on the coffee shop page: 25 → 0, [PR #1](https://github.com/PugarHuda/jangkau/pull/1) with the report as its description |
| The agent recovers | v4 trace `8ad9968f…`: a malformed JSON reply is retried, and a `page-has-heading-one` edit that broke `heading-order` is rejected, rolled back and fixed on the next attempt |
| Built in public | _TODO: #neatHack tweets_ |
| Code written during the hackathon | Commit history of this repo (Oct 10–12, 2026) |
