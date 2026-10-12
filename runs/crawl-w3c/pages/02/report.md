# Jangkau audit (v5)

Target: `runs\crawl-w3c\pages\02\source\index.html`
Failing elements: **46** across 2 rules

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `landmark-one-main` | moderate | - | best practice | - | 1 | 1 |
| `region` | moderate | - | best practice | - | 45 | 45 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **4**

| Technique | Message | Element |
|---|---|---|
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="p" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="o" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="u" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
| `1_3_1.H43,H63` | The relationship between td elements and their associated th elements is not defined. Use either the scope attribute on th elements, or the headers attribute on td elements. | `<table id="r" class="report script_on script_on"> <caption>Conformance of Home Page to WCA` |
