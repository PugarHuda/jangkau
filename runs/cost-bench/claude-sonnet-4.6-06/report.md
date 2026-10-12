# Jangkau report (v8-bench, verify=True)

Target: `C:\Users\pc\AppData\Local\Temp\claude\C--Hackathons-Hackathon-neatlogs\17763b5f-f1ab-4a15-b6ee-c88003ac10d5\scratchpad\startbootstrap-freelancer\dist\index.html`  
neatlogs trace: `433d7f800c3fd3efbabdf373cda2809c`

| Metric | Value |
|---|---|
| Failing nodes before | 33 |
| Failing nodes after | 0 |
| Reduction | 100% |
| LLM calls | 7 |
| Tokens (in/out) | 58186 / 2560 |
| Cost (reported by the LiteLLM gateway) | $0.2343 (claude-sonnet-4.6: 7 calls, $0.2343) |
| Budget stop | no |
| Wall time | 48.7s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `color-contrast` | fixed | 2 | 7 → 0 |
| `link-name` | fixed | 1 | 4 → 0 |
| `heading-order` | fixed | 1 | 1 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `region` | fixed | 2 | 20 → 0 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 7 | 0 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 4 | 0 |
| `heading-order` | moderate | - | best practice | - | 1 | 0 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 20 | 0 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **15 → 4**

| Technique | Message | Element |
|---|---|---|
| `2_4_1.G1,G123,G124` | This link points to a named anchor "!" within the document, but no anchor exists with that name. | `<a class="btn btn-outline-light btn-social mx-1" href="#!" aria-label="Facebook"><svg clas` |
| `2_4_1.G1,G123,G124` | This link points to a named anchor "!" within the document, but no anchor exists with that name. | `<a class="btn btn-outline-light btn-social mx-1" href="#!" aria-label="Twitter"><svg class` |
| `2_4_1.G1,G123,G124` | This link points to a named anchor "!" within the document, but no anchor exists with that name. | `<a class="btn btn-outline-light btn-social mx-1" href="#!" aria-label="LinkedIn"><svg clas` |
| `2_4_1.G1,G123,G124` | This link points to a named anchor "!" within the document, but no anchor exists with that name. | `<a class="btn btn-outline-light btn-social mx-1" href="#!" aria-label="Dribbble"><svg clas` |

System prompt: `jangkau-fixer-system@v1 (production)`  
neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
