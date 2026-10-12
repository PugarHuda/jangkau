# Jangkau site fix (v8-site)

Start: https://www.w3.org/WAI/demos/bad/before/home.html
Pages fixed: **3**, failing elements **210 → 6**, cost **$0.5300**
(reported by the LiteLLM gateway), cap $0.25 per page
neatlogs trace (one for the whole site run, a jangkau_run span per page): https://app.neatlogs.com/traces/02115b3732468385dfad168829c2f061?orgId=7d30cb27-b8a1-4558-a9bd-862b4c76999c&projectId=a7383f92-712a-4139-a767-58f3245b56cd

| Page | Failing elements | LLM calls | Cost | Details |
|---|---|---|---|---|
| [https://www.w3.org/WAI/demos/bad/before/home.html](https://www.w3.org/WAI/demos/bad/before/home.html) | 81 → 0 | 13 | $0.2124 | [report](pages/01/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/reports/home.html](https://www.w3.org/WAI/demos/bad/before/reports/home.html) | 46 → 0 | 2 | $0.0622 | [report](pages/02/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/annotated/home.html](https://www.w3.org/WAI/demos/bad/before/annotated/home.html) | 83 → 6 | 12 | $0.2554 (capped) | [report](pages/03/report.md) |
