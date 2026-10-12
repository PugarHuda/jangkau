# Jangkau report (v6-video, verify=True)

Target: `demo_site\toko.html`  
neatlogs trace: `848da8cc19d5cbe2fa3a4f1128f8237e`

| Metric | Value |
|---|---|
| Failing nodes before | 47 |
| Failing nodes after | 0 |
| Reduction | 100% |
| LLM calls | 15 |
| Tokens (in/out) | 30433 / 5457 |
| Wall time | 76.2s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `button-name` | fixed | 1 | 1 → 0 |
| `image-alt` | fixed | 1 | 6 → 0 |
| `label` | fixed | 1 | 3 → 0 |
| `aria-hidden-focus` | fixed | 1 | 1 → 0 |
| `color-contrast` | fixed | 2 | 18 → 0 |
| `document-title` | fixed | 1 | 1 → 0 |
| `frame-title` | fixed | 1 | 1 → 0 |
| `html-has-lang` | fixed | 1 | 1 → 0 |
| `heading-order` | fixed | 1 | 1 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `meta-viewport` | fixed | 1 | 1 → 0 |
| `page-has-heading-one` | fixed | 2 | 1 → 0 |
| `region` | fixed | 1 | 10 → 0 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `button-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `image-alt` | critical | 1.1.1 | A | 9.1.1.1 | 6 | 0 |
| `label` | critical | 4.1.2 | A | 9.4.1.2 | 3 | 0 |
| `aria-hidden-focus` | serious | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 18 | 0 |
| `document-title` | serious | 2.4.2 | A | 9.2.4.2 | 1 | 0 |
| `frame-title` | serious | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `html-has-lang` | serious | 3.1.1 | A | 9.3.1.1 | 1 | 0 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 1 | 0 |
| `heading-order` | moderate | - | best practice | - | 1 | 0 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `meta-viewport` | moderate | 1.4.4 | AA | 9.1.4.4 | 1 | 0 |
| `page-has-heading-one` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 10 | 0 |

neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
