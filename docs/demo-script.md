# Demo video script (2:09, X free accounts cap at 2:20)

The organisers asked for one video covering: the problem, how cfo.ai and Entire were part of the project,
and how neatlogs was used to identify and resolve the incidents the agent ran into. The middle block is the longest on purpose.

| Time | Screen | Voice-over |
|---|---|---|
| 0:00–0:16 | The shop page next to its real accessibility tree; 47 failures; European Accessibility Act tag | "One in six people lives with a disability. To a screen reader, this online shop sounds like: image. Link. Image. Forty-seven accessibility failures. And in Europe, since June 2025, that's a legal problem." |
| 0:16–0:28 | A real `jangkau.py demo_site/shop.html` run replayed at 7×, next to the fixed accessibility tree | "Jangkau is an agent that doesn't just audit the page. It fixes it. Every edit is re-checked in a real browser, and if it breaks anything, it's rolled back and tried again." |
| 0:28–0:36 | neatlogs trace (workflow, agent and tool spans), then Detections | "We traced every run with neatlogs, then set up a detection that flags each rule the agent failed to fix. Here's what it caught." |
| 0:36–0:51 | `label` span: `new violations: {'region': 13}`, then bars v1 10 / v2 14 / v4 0 | "Incident one. Our first verifier rejected correct label fixes. The span told us why: it counted rules still waiting in the queue as breakage. We fixed the check, and the shop went from forty-seven failures to zero." |
| 0:51–1:10 | Freelancer `color-contrast` span, then `compare.png` before/after, 33 → 0 | "Incident two, on a real Bootstrap template. Contrast fixes kept failing. The traces showed a pixel diff punishing correct recolors, and then a hidden opacity of zero point six five. Edge-map diffs, measured feedback, and escalation to a stronger model took it from thirty-three to zero." |
| 1:10–1:25 | Execution Failed on `apply_edits`, then the W3C page before/after, 67 → 4 | "Incident three, on the W3C's own inaccessible demo page. The Execution Failed detection caught one bad edit throwing away nineteen good ones. Now valid edits are kept: sixty-seven failures down to four." |
| 1:25–1:37 | GitHub Actions runs, then code scanning alerts with WCAG and EN 301 549 tags | "It also runs in CI, as a GitHub Action. Every failure lands in code scanning, mapped to WCAG and to the European standard, EN 301 549." |
| 1:37–1:48 | `--explain` on the live fixed page, then the commit statuses of a deploy (`Vercel`, `jangkau/accessibility`) | "Every fix is traceable. The fixed page carries a stamp that leads back to its neatlogs trace, and every Vercel deploy is re-checked before it gets a green status." |
| 1:48–1:54 | Entire checkpoint page for a commit | "Entire recorded the coding sessions behind these fixes, as checkpoints on our commits." |
| 1:54–2:05 | cfo.ai model: Base / Growth / Downside | "And cfo.ai modeled the business on measured costs: about nine cents per page, an eighty-four percent gross margin, and a downside case that set our per-page spend cap." |
| 2:05–2:09 | Jangkau, jangkau-jet.vercel.app · github.com/PugarHuda/jangkau | "Jangkau. So the web reaches everyone." |
