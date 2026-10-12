# Jangkau report (v8-site, verify=True)

Target: `runs\site-fix-w3c\pages\01\source\index.html`  
neatlogs trace: https://app.neatlogs.com/traces/02115b3732468385dfad168829c2f061?orgId=7d30cb27-b8a1-4558-a9bd-862b4c76999c&projectId=a7383f92-712a-4139-a767-58f3245b56cd

| Metric | Value |
|---|---|
| Failing nodes before | 81 |
| Failing nodes after | 0 |
| Reduction | 100% |
| LLM calls | 13 |
| Tokens (in/out) | 118792 / 10599 |
| Cost (reported by the LiteLLM gateway) | $0.2124 (claude-haiku: 12 calls, $0.1773, claude-sonnet-4.6: 1 calls, $0.0351) |
| Budget stop | no |
| Wall time | 104.4s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `image-alt` | fixed | 5 | 33 → 0 |
| `select-name` | fixed | 1 | 1 → 0 |
| `color-contrast` | fixed | 1 | 2 → 0 |
| `html-has-lang` | fixed | 1 | 1 → 0 |
| `link-name` | fixed | 1 | 7 → 0 |
| `focus-not-removed` | fixed | 1 | 14 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `region` | fixed | 2 | 22 → 0 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `image-alt` | critical | 1.1.1 | A | 9.1.1.1 | 33 | 0 |
| `select-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 2 | 0 |
| `html-has-lang` | serious | 3.1.1 | A | 9.3.1.1 | 1 | 0 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 7 | 0 |
| `focus-not-removed` | serious | 2.1.1, 2.4.7 | A | 9.2.1.1, 9.2.4.7 | 14 | 0 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 22 | 0 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **41 → 3**

| Technique | Message | Element |
|---|---|---|
| `1_1_1.H30` | Img element is the only content of the link, but is missing alt text. The alt text should describe the purpose of the link. | `<a href="news.html" aria-label="Read more about heat wave linked to temperatures"><img src` |
| `1_1_1.H30` | Img element is the only content of the link, but is missing alt text. The alt text should describe the purpose of the link. | `<a href="news.html" aria-label="Read more about man gets nine months in violin case"><img ` |
| `1_1_1.H30` | Img element is the only content of the link, but is missing alt text. The alt text should describe the purpose of the link. | `<a href="news.html" aria-label="Read more about lack of brains hinders research"><img src=` |

System prompt: `jangkau-fixer-system@v1 (production)`  
neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
