# Jangkau audit (v5)

Target: `runs\crawl-w3c\pages\05\source\index.html`
Failing elements: **52** across 9 rules

| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |
|---|---|---|---|---|---|---|
| `image-alt` | critical | 1.1.1 | A | 9.1.1.1 | 26 | 26 |
| `select-name` | critical | 4.1.2 | A | 9.4.1.2 | 1 | 1 |
| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 8 | 8 |
| `html-has-lang` | serious | 3.1.1 | A | 9.3.1.1 | 1 | 1 |
| `link-name` | serious | 2.4.4, 4.1.2 | A | 9.2.4.4, 9.4.1.2 | 4 | 4 |
| `focus-not-removed` | serious | 2.1.1, 2.4.7 | A | 9.2.1.1, 9.2.4.7 | 4 | 4 |
| `landmark-one-main` | moderate | - | best practice | - | 1 | 1 |
| `region` | moderate | - | best practice | - | 6 | 6 |
| `empty-table-header` | minor | - | best practice | - | 1 | 1 |

## Independent cross-check (HTML_CodeSniffer, WCAG2AA)

A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. HTML_CodeSniffer errors: **38**

| Technique | Message | Element |
|---|---|---|
| `3_1_1.H57` | The html element should have a lang or xml:lang attribute which describes the language of the document. | `<html><head><base href="https://www.w3.org/WAI/demos/bad/before/tickets.html"> <title>Welc` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/border_left_top.gif" width="10px" height="10px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/border_top.gif" height="10px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/border_right_top.gif" width="10px" height="10px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/border_left.gif" width="10px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/top_logo_next_end.gif" width="24px" height="86px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/top_weather.gif" width="128px" height="86px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/top_logo_next_start.gif" width="22px" height="86px">` |
| `4_1_2.H91` | This select element does not have a name available to an accessibility API. Valid names are: label element, title undefined, aria-label undefined, aria-labelledby undefined. | `<select onchange="location.href = this.value;"> <option selected="">QUICKMENU ----&gt; </o` |
| `1_3_1.F68` | This form field should be labelled in some way. Use the label element (either with a "for" attribute or wrapped around the form field), or "title", "aria-label" or "aria-labelledby" attributes as appr | `<select onchange="location.href = this.value;"> <option selected="">QUICKMENU ----&gt; </o` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src="./img/mark.gif" width="158px" height="7px">` |
| `1_1_1.H37` | Img element missing an alt attribute. Use the alt attribute to specify a short text alternative. | `<img src=".img/marker2_w.gif" width="78px" height="1px">` |
