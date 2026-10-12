# Jangkau report (v8-bench, verify=True)

Target: `demo_site\index.html`  
neatlogs trace: `930cb11f63cd3047ada41ebc1daf9853`

| Metric | Value |
|---|---|
| Failing nodes before | 25 |
| Failing nodes after | 0 |
| Reduction | 100% |
| LLM calls | 8 |
| Tokens (in/out) | 11854 / 1502 |
| Cost (reported by the LiteLLM gateway) | $0.0639 (claude-sonnet-4.6: 8 calls, $0.0639) |
| Budget stop | no |
| Wall time | 23.4s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `button-name` | fixed | 1 | 1 → 0 |
| `image-alt` | fixed | 1 | 5 → 0 |
| `select-name` | fixed | 1 | 1 → 0 |
| `color-contrast` | fixed | 1 | 8 → 0 |
| `document-title` | fixed | 1 | 1 → 0 |
| `html-has-lang` | fixed | 1 | 1 → 0 |
| `heading-order` | fixed | 1 | 1 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `button-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `image-alt` | critical | 1.1.1 | A | 9.1.1.1 | 5 | 0 |
| `select-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 0 |
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 8 | 0 |
| `document-title` | serious | 2.4.2 | A | 9.2.4.2 | 1 | 0 |
| `html-has-lang` | serious | 3.1.1 | A | 9.3.1.1 | 1 | 0 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 1 | 0 |
| `heading-order` | moderate | - | best practice | - | 1 | 0 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 5 | 0 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **21 → 3**

| Technique | Message | Element |
|---|---|---|
| `4_1_2.H91` | This textinput element does not have a name available to an accessibility API. Valid names are: label element, title undefined, aria-label undefined, aria-labelledby undefined. | `<input type="text" placeholder="Name" style="">` |
| `1_3_1.F68` | This form field should be labelled in some way. Use the label element (either with a "for" attribute or wrapped around the form field), or "title", "aria-label" or "aria-labelledby" attributes as appr | `<input type="text" placeholder="Name" style="">` |
| `4_1_2.H91` | This telinput element does not have a name available to an accessibility API. Valid names are: label element, title undefined, aria-label undefined, aria-labelledby undefined. | `<input type="tel" placeholder="WhatsApp number" style="">` |

System prompt: `jangkau-fixer-system@v1 (production)`  
neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
