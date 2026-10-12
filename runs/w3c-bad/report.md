# Jangkau report (v6-w3c, verify=True)

Target: `runs\w3c-bad\source\index.html`  
neatlogs trace: `2d5650d366105b38449d868f3b1d74cd`

| Metric | Value |
|---|---|
| Failing nodes before | 67 |
| Failing nodes after | 4 |
| Reduction | 94% |
| LLM calls | 11 |
| Tokens (in/out) | 100293 / 11384 |
| Wall time | 93.6s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `image-alt` | fixed | 2 | 33 → 0 |
| `select-name` | fixed | 1 | 1 → 0 |
| `color-contrast` | fixed | 1 | 2 → 0 |
| `html-has-lang` | fixed | 1 | 1 → 0 |
| `link-name` | fixed | 1 | 7 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `region` | partial | 4 | 22 → 4 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `image-alt` | critical | 1.1.1 | A | 9.1.1.1 | 33 | 0 |
| `select-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 2 | 0 |
| `html-has-lang` | serious | 3.1.1 | A | 9.3.1.1 | 1 | 0 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 7 | 0 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 22 | 4 |

neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
