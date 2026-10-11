# Jangkau report (v2, verify=True)

Target: `demo_site\toko.html`

| Metric | Value |
|---|---|
| Failing nodes before | 47 |
| Failing nodes after | 14 |
| Reduction | 70% |
| LLM calls | 18 |
| Tokens (in/out) | 35944 / 5187 |
| Wall time | 76.4s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
| `button-name` | fixed | 2 | 1 → 0 |
| `image-alt` | fixed | 1 | 6 → 0 |
| `label` | gave-up | 3 | 3 → 3 |
| `aria-hidden-focus` | fixed | 1 | 1 → 0 |
| `color-contrast` | fixed | 1 | 18 → 9 |
| `document-title` | fixed | 1 | 1 → 0 |
| `frame-title` | fixed | 1 | 1 → 0 |
| `html-has-lang` | fixed | 1 | 1 → 0 |
| `heading-order` | fixed | 1 | 1 → 0 |
| `landmark-one-main` | fixed | 1 | 1 → 0 |
| `meta-viewport` | fixed | 1 | 1 → 0 |
| `page-has-heading-one` | gave-up | 3 | 1 → 1 |
| `region` | fixed | 1 | 10 → 1 |
