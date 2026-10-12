# Jangkau report (v8-site, verify=True)

Target: `runs\site-fix-w3c\pages\02\source\index.html`  
neatlogs trace: https://app.neatlogs.com/traces/02115b3732468385dfad168829c2f061?orgId=7d30cb27-b8a1-4558-a9bd-862b4c76999c&projectId=a7383f92-712a-4139-a767-58f3245b56cd

| Metric | Value |
|---|---|
| Failing nodes before | 46 |
| Failing nodes after | 0 |
| Reduction | 100% |
| LLM calls | 2 |
| Tokens (in/out) | 53102 / 696 |
| Cost (reported by the LiteLLM gateway) | $0.0622 (claude-haiku: 2 calls, $0.0622) |
| Budget stop | no |
| Wall time | 17.1s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `region` | fixed | 1 | 45 → 0 |

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `landmark-one-main` | moderate | - | best practice | - | 1 | 0 |
| `region` | moderate | - | best practice | - | 45 | 0 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **4 → 4**

| Technique | Message | Element |
|---|---|---|
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="p" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="o" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="u" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="r" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |

System prompt: `jangkau-fixer-system@v1 (production)`  
neatlogs delivery: `{"span_queue_drops": 0, "log_queue_drops": 0, "span_export_failures": 0, "log_export_failures": 0, "masked_span_drops": 0, "masked_log_drops": 0, "span_capture_truncations": 0, "log_capture_truncations": 0, "span_overflow_exports": 0, "span_overflow_failures": 0, "span_overflow_unavailable": 0, "log_overflow_exports": 0, "log_overflow_failures": 0, "log_overflow_unavailable": 0, "span_upload_authority_available": false, "log_upload_authority_available": false, "span_upload_authority_reason": "backend_upload_contract_unavailable", "log_upload_authority_reason": "backend_upload_contract_unavailable", "span_media_uploads": 0, "span_media_upload_failures": 0, "log_media_uploads": 0, "log_media_upload_failures": 0, "upload_last_failure_reason": ""}`
