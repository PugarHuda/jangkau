# Jangkau site audit (v5)

Start: https://www.w3.org/WAI/demos/bad/before/home.html
Pages audited: **5**, failing elements: **318**

| Page | axe failing elements | Rules | HTML_CodeSniffer errors | Details |
|---|---|---|---|---|
| [https://www.w3.org/WAI/demos/bad/before/home.html](https://www.w3.org/WAI/demos/bad/before/home.html) | 81 | 8 | 41 | [report](pages/01/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/reports/home.html](https://www.w3.org/WAI/demos/bad/before/reports/home.html) | 46 | 2 | 4 | [report](pages/02/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/annotated/home.html](https://www.w3.org/WAI/demos/bad/before/annotated/home.html) | 83 | 8 | 41 | [report](pages/03/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/news.html](https://www.w3.org/WAI/demos/bad/before/news.html) | 56 | 7 | 42 | [report](pages/04/report.md) |
| [https://www.w3.org/WAI/demos/bad/before/tickets.html](https://www.w3.org/WAI/demos/bad/before/tickets.html) | 52 | 9 | 38 | [report](pages/05/report.md) |

## Rules across the site

| Rule | Impact | WCAG SC | EN 301 549 | Pages | Elements |
|---|---|---|---|---|---|
| `image-alt` | critical | 1.1.1 | 9.1.1.1 | 4/5 | 131 |
| `select-name` | critical | 4.1.2 | 9.4.1.2 | 4/5 | 4 |
| `focus-not-removed` | serious | 2.1.1, 2.4.7 | 9.2.1.1, 9.2.4.7 | 4/5 | 36 |
| `link-name` | serious | 2.4.4, 4.1.2 | 9.2.4.4, 9.4.1.2 | 4/5 | 22 |
| `html-has-lang` | serious | 3.1.1 | 9.3.1.1 | 4/5 | 4 |
| `color-contrast` | serious | 1.4.3 | 9.1.4.3 | 3/5 | 12 |
| `region` | moderate | - | - | 5/5 | 103 |
| `landmark-one-main` | moderate | - | - | 5/5 | 5 |
| `empty-table-header` | minor | - | - | 1/5 | 1 |
