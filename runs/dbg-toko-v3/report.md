# Jangkau report (v3, verify=True)

Target: `demo_site\toko.html`

| Metric | Value |
|---|---|
| Failing nodes before | 47 |
| Failing nodes after | 1 |
| Reduction | 98% |
| LLM calls | 18 |
| Tokens (in/out) | 36937 / 5274 |
| Wall time | 81.0s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `button-name` | fixed | 2 | 1 → 0 |
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
| `page-has-heading-one` | gave-up | 3 | 1 → 1 |
| `region` | fixed | 2 | 10 → 0 |
