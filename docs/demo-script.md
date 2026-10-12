# Demo video script (target 2:00, X free accounts cap at 2:20)

| Time | Screen | Voice-over |
|---|---|---|
| 0:00–0:12 | Batik shop page, screen reader reading "image, image, button" | "1 in 6 people live with a disability. To a screen reader, this shop is 'image, image, button'. 47 WCAG failures." |
| 0:12–0:25 | `python jangkau.py demo_site/toko.html` starting | "Jangkau is an agent that fixes the page, not just audits it, and proves every fix." |
| 0:25–0:50 | Terminal: a rejected attempt + revert; neatlogs span tree of `fix_rule` | "Each fix must pass five checks: the rule improves, nothing else breaks, no content is deleted, no landmark is left empty, the page looks the same. Fail one and it rolls back and retries with the reason." |
| 0:50–1:15 | neatlogs: v2 trace (13 left) next to v4 trace (0 left) | "Our first verifier made things worse: 13 failures left. The traces showed why: it rejected correct fixes and stopped on partial ones. Three fixes later: 47 to 0, with fewer LLM calls." |
| 1:15–1:30 | `runs/real-freelancer/compare.png`, then [PR #1](https://github.com/PugarHuda/jangkau/pull/1) | "Not just our demo page: StartBootstrap Freelancer, unmodified. 33 failing nodes to 0 in 40 seconds, layout unchanged. Add `--pr` and it opens a pull request with the report." |
| 1:30–1:45 | Entire checkpoint page + `docs/entire-graph.md` | "Entire kept the context behind every change to the agent, and Entire Graph showed the blast radius before we touched the verifier." |
| 1:45–2:00 | cfo.ai model | "About $0.06 per page. At $29 a month, that is a 90% margin. Jangkau: so the web reaches everyone." |
