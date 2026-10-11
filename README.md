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
       │    4. the page still looks the same (pixel diff ≤ 35%)
       ├─ any check fails ──► revert, retry with the reason (max 3)
       └─ checkpoint state.json (an interrupted run resumes)
final audit ──► report.md (before/after, tokens, time)
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
python -m pytest -q
```

`demo_site/` is a small coffee shop page with 25 failing nodes across 10 WCAG rules.

## Evidence for judges

| Claim | Evidence |
|---|---|
| The agent improved | Same page (`demo_site/toko.html`, 47 failing nodes), same model (claude-haiku), traced in neatlogs and filtered by tag `version:v1` / `version:v2` / `version:v4`. **v1** (no checks): 10 left, 14 LLM calls. **v2** (first verifier): 14 left, 18 calls. **v4**: **0 left**, 16 calls. Reports in `runs/ev-*/report.md`. Root causes are in [hackathon.md](hackathon.md) |
| We used neatlogs | Each run is a `jangkau_run` workflow trace with `fix_rule` agent spans, `audit` / `apply_edits` / `visual_diff` tool spans and auto-captured LLM calls. Trace IDs: v1 `002efc98d1c3610e269f95108e5371d4`, v4 `8ad9968fc9a602e0dad474b24842835f`. SDK Doctor probe: PASS |
| We used Entire | [Entire Graph impact + diff](docs/entire-graph.md) for the verifier changes. Checkpoints on `entire/checkpoints/v1`: _TODO link + ID_ |
| We used cfo.ai | [BUSINESS.md](BUSINESS.md) + the cfo.ai model. _TODO: link/screenshot_ |
| The agent recovers | v4 trace `8ad9968f…`: a malformed JSON reply is retried, and a `page-has-heading-one` edit that broke `heading-order` is rejected, rolled back and fixed on the next attempt |
| Built in public | _TODO: #neatHack tweets_ |
| Code written during the hackathon | Commit history of this repo (Oct 10–12, 2026) |
