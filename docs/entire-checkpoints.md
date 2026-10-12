# Entire checkpoints: progress and key decisions

Every Claude Code session in this repo was recorded by Entire. Each commit carries an `Entire-Checkpoint` trailer that
links it to the session (prompts, responses, files touched) that produced it. Checkpoints are stored as git refs and
browsable at https://entire.io/gh/PugarHuda/jangkau.

Commits from Oct 10–11 predate Entire being enabled in this repo, so they have no checkpoint.

The **Decision** column covers the checkpoints where the direction changed, and why. Most decisions came from
evidence: a neatlogs detection, a cfo.ai scenario or an `entire graph` impact check.

| When (WIB) | Checkpoint | Commit | Decision |
|---|---|---|---|
| Oct 12 09:31 | [`01M4PZ7CYXWQQTTBCQ1QKJ075N`](https://entire.io/gh/PugarHuda/jangkau/commit/9713fcd8e88c8a88519e718dc8e8ac2c7ea883f8) | README: Entire checkpoint evidence |  |
| Oct 12 09:32 | [`01M4PZ8AJ785GSHFD0R2Q8KVHN`](https://entire.io/gh/PugarHuda/jangkau/commit/6eaf224ded18b2e6c782810e015ccdad3c9acaca) | README: link Entire checkpoint |  |
| Oct 12 09:48 | [`01M4Q0645XBA640F6XEZKKD7FM`](https://entire.io/gh/PugarHuda/jangkau/commit/e05c5025cb1d67b43a915b3d6473c446380d91f3) | cfo.ai model: 24-month plan with Base, Growth and Downside scenarios | **cfo.ai:** Model the business in cfo.ai before pricing: Base / Growth / Downside over 24 months. |
| Oct 12 09:58 | [`01M4Q0QTQK2ZSTVPW5C7G5WVP4`](https://entire.io/gh/PugarHuda/jangkau/commit/cfc93d6d59519a4054f92ebe6b91b82f42ce20c7) | Link the cfo.ai model |  |
| Oct 12 10:05 | [`01M4Q15V8VZ1Q0P99KNVBDNCQY`](https://entire.io/gh/PugarHuda/jangkau/commit/bb147e46d32fc565b4570a9e2aa02ab757659c52) | README: five checks, v5, Entire repo link |  |
| Oct 12 10:15 | [`01M4Q1QWZPZXJ1AWJWGSPZD2BW`](https://entire.io/gh/PugarHuda/jangkau/commit/75f51e00f1f5332c2d1c123903108fd6bf379995) | Link v5 neatlogs trace; stop tests from exporting traces |  |
| Oct 12 10:23 | [`01M4Q25NR2SQV97J0475AQ0GC5`](https://entire.io/gh/PugarHuda/jangkau/commit/9e6c3b91e1412438b5971db6e79c33bdb8fd40c0) | README: neatlogs trace screenshots (span tree, retry, recovery reasoning) |  |
| Oct 12 10:36 | [`01M4Q2Y68WGMDJJ4DJ3A5FAKV0`](https://entire.io/gh/PugarHuda/jangkau/commit/d349afa1a4ab3157fd28d65019d06eb5c9ffdf51) | Audit-only mode, SARIF for code scanning, EN 301 549 mapping, URL input, GitHub Action | **Scope:** Add an audit-only mode that needs no model key, so CI and code scanning (SARIF) can run on any repo without secrets. Map every rule to WCAG and EN 301 549, the standard behind the European Accessibility Act. |
| Oct 12 10:41 | [`01M4Q37GYR97DYJ7MFHY8AV051`](https://entire.io/gh/PugarHuda/jangkau/commit/2f89b69f28a2b7ad5bee3889efd7d72859c25b9a) | Keep valid edits from a batch, progress-based retry budget, escalate when stuck, --wait | **Agent:** Incident 4 from neatlogs: one mistyped `find` threw away 19 good edits. Decision: keep each valid edit from a batch, let progress earn more attempts, and escalate to a stronger model after two stuck attempts in a row. |
| Oct 12 10:44 | [`01M4Q3BWZXFNFJXKXMX91J0DWV`](https://entire.io/gh/PugarHuda/jangkau/commit/85e8e6d110e6b1ae1743dd8ac7bbcbb158863552) | W3C BAD demo run (67 -> 4), docs for CI, SARIF, EN 301 549 and URL mode | **Result:** W3C's inaccessible demo went from 67 → 26 to 67 → 4 with the change above. |
| Oct 12 10:44 | [`01M4Q3CCD165S5N9GW4FXK32KC`](https://entire.io/gh/PugarHuda/jangkau/commit/03de7b51e309ce53d3b8d22a9ca93d75b72c9175) | Remove stray patch script |  |
| Oct 12 10:57 | [`01M4Q43YBHQDQ3NSNYHQWHYZH4`](https://entire.io/gh/PugarHuda/jangkau/commit/14d4a9be2a5f114888bd10fea4f3f952ba92c7d0) | neatlogs incident write-up: detections, root causes, fixes, one still open | **Honesty:** Write up each neatlogs incident, including the one that is still open (landmarks in table layouts), rather than hide it. |
| Oct 12 10:58 | [`01M4Q45XS2HKPF8PVB5V1HFWZT`](https://entire.io/gh/PugarHuda/jangkau/commit/9371ccec84910fea8c9bc6413a65c49d92862a00) | Landing: W3C live-URL result and the GitHub Action |  |
| Oct 12 11:54 | [`01M4Q7CHS6TQK4F5BQCS76ET8N`](https://entire.io/gh/PugarHuda/jangkau/commit/f5ad973db6403c02e7a36830aa9a6187d5eb44b9) | Demo video: Remotion composition over real captures, Kokoro voice-over, captions |  |
| Oct 12 12:09 | [`01M4Q87C2Z8CKD46KJ91NJE3CM`](https://entire.io/gh/PugarHuda/jangkau/commit/456fea7b70721a2b40f236c905fe584ec6eae32d) | Second engine, custom F55 rule, site crawl, prompt registry | **Agent:** Add a second engine (HTML_CodeSniffer) as a cross-check. It surfaced `onfocus=blur()`, which neither engine flags, so we wrote a custom axe rule for it (WCAG failure F55). |
| Oct 12 15:17 | [`01M4QK02SH139QSD9DR0ZJDJFH`](https://entire.io/gh/PugarHuda/jangkau/commit/233701a6de648b4cd79a629ba9998086efb84dc3) | Demo pages in English, same markup and same 25 / 47 violations |  |
| Oct 12 15:28 | [`01M4QKMBPWGQQNVREMM3WMBEST`](https://entire.io/gh/PugarHuda/jangkau/commit/3bafb8209d44b7971836c5fe8f780a99840270de) | Everything in English: demo file names, ids and image names too |  |
| Oct 12 15:46 | [`01M4QMP59HGZEJ33YFSKWA68J1`](https://entire.io/gh/PugarHuda/jangkau/commit/d22218cc5a8d33088b9c2d6518ba6af4a8798b05) | Video re-rendered from the all-English demo: new captures, trace and alerts |  |
| Oct 12 16:00 | [`01M4QNEY1FHWDEZD22SR510941`](https://entire.io/gh/PugarHuda/jangkau/commit/d57c54ab808842be1a3d7e17e39b916b48b65761) | Audit the deployment Vercel reports, not the one before it; real cost per run; budget cap | **Cost:** The Downside scenario in cfo.ai ran out of cash, so we added a hard per-page spend cap (`--max-cost`) and read the real cost of every call from the gateway. |
| Oct 12 16:05 | [`01M4QNRM27CHDKN29PYJDBF1YV`](https://entire.io/gh/PugarHuda/jangkau/commit/b368ddcb100c7353ec2fbfd28d4b28fd1ceb8c11) | Measured cost per page: 8 full runs, 4 real pages, both models, all to 0 | **Cost:** Replace the assumed cost with a measured one: 8 full runs on 4 real pages. Haiku averaged $0.09 per page, and those numbers went back into the cfo.ai model. |
| Oct 12 16:15 | [`01M4QPBGB6BH1R4FTA4TV6K66Q`](https://entire.io/gh/PugarHuda/jangkau/commit/89399e15f93e8156c98d865446f38d5c656c6203) | Provenance across tools: every fix leads back to its agent run | **Provenance:** Borrow Entire's trailer pattern for the product itself: Jangkau's PR commits carry `Jangkau-Trace` / `Jangkau-Prompt` / `Jangkau-Result`, so a fixed line leads back to its agent run. |
| Oct 12 16:19 | [`01M4QPJ60S0F4GKH3QP9Y1PVJQ`](https://entire.io/gh/PugarHuda/jangkau/commit/2cb0f5974aa548277b46166e4bdd4bb191539b52) | Don't copy the target repo's .git into the run folder |  |
| Oct 12 16:24 | [`01M4QPTQZ41SHVR9MERTQH6DFF`](https://entire.io/gh/PugarHuda/jangkau/commit/9b09d517f393b2ab7ba11c052c69771b8c000a57) | Send the Vercel bypass secret to the audited host only | **Security:** A background security review flagged the Vercel bypass secret being sent to every crawled host. It is now sent only to the audited deployment's host. |
| Oct 12 16:58 | [`01M4QRSPVKK5TF02NP29N8BRV2`](https://entire.io/gh/PugarHuda/jangkau/commit/889beae3efad0aa4d4f58626fed0843890e0619d) | hackathon.md: mark what is done, list what is left |  |
| Oct 12 20:50 | [`01M4R62ENFM5D7KN4E1P0MPF23`](https://entire.io/gh/PugarHuda/jangkau/commit/668bdc1e36ece143ee2e30ca9bdb25cba4239060) | Fix whole sites (--crawl --fix) and land contrast fixes in the source CSS | **Agent:** Before changing `fix_rule` we checked its blast radius with `entire graph impact` (`run` has 37 dependents), then verified the tests against a baseline. The change: fix whole sites, and land contrast fixes on the site's CSS design tokens instead of inline overrides. |
| Oct 12 20:59 | [`01M4R6KBB408AKT92DZ3256AMS`](https://entire.io/gh/PugarHuda/jangkau/commit/be338a6f04605b02ab1afd9c4a8a14f53c5c3027) | Demo video: provenance and deploy-status scene (2:09) |  |

## Using checkpoints to review agent work

- `entire graph checkpoint <id>` lists the functions a checkpoint changed and how many dependents each has
  (see [entire-graph.md](entire-graph.md)).
- `entire jangkau <id>` ([our plugin](../entire-plugin/README.md)) audits every page the checkpoint touched, before
  and after, and exits 1 if accessibility got worse.
