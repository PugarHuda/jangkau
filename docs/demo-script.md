# Demo video script (target 2:00, X free accounts cap at 2:20)

The organisers asked for one video covering: the problem, how cfo.ai and Entire were part of the project,
and how neatlogs was used to identify and resolve the incidents the agent ran into. The middle block is the longest on purpose.

| Time | Screen | Voice-over |
|---|---|---|
| 0:00–0:12 | Batik shop page, screen reader reading "image, image, button" | "1 in 6 people live with a disability. To a screen reader, this shop is 'image, image, button'. 47 WCAG failures, and in the EU that's now a legal problem." |
| 0:12–0:25 | `python jangkau.py demo_site/toko.html` starting | "Jangkau is an agent that fixes the page, not just audits it. Every edit is re-audited and rolled back if it breaks anything." |
| 0:25–0:40 | neatlogs → Detections → **Rule left unfixed**, flagged spans list | "neatlogs flags every rule the agent failed to fix. Here's each incident it caught." |
| 0:40–0:55 | Click the v2 `label` span: `new violations: {'region': 13}`, then the v4 trace at 0 | "Incident one: our verifier rejected correct label fixes. The span said why. We fixed the check: 47 to 0." |
| 0:55–1:10 | Freelancer span: `color-contrast` partial → v5 trace, Sonnet escalation, `compare.png` | "Incident two, a real Bootstrap site: contrast fixes kept failing. The traces showed a pixel diff punishing correct recolours, then a hidden 0.65 opacity. Edge-map diff, measured feedback, escalation: 33 to 0." |
| 1:10–1:22 | Detections → **Execution Failed** on `apply_edits`, then the W3C run 67 → 4 | "Incident three, W3C's own inaccessible demo page: one bad edit threw away 19 good ones. Now valid edits are kept: 67 to 4." |
| 1:22–1:32 | GitHub → Security → Code scanning alerts, `accessibility.yml` | "And it runs in CI: SARIF in GitHub code scanning, each alert mapped to WCAG and EN 301 549." |
| 1:32–1:45 | Entire checkpoint page + `docs/entire-graph.md` | "Entire recorded every agent session behind these fixes, and Entire Graph showed the blast radius before we touched the verifier." |
| 1:45–2:00 | cfo.ai model, Base / Growth / Downside | "cfo.ai modelled the business: $0.06 per page, 83% gross margin, and the downside case that set our fair-use rule. Jangkau: so the web reaches everyone." |
