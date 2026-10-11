# Entire Graph evidence

Generated with entire-graph v0.4.0. Used to check the blast radius before changing the verifier (`fix_rule`) and to list what each iteration changed.

## `entire graph impact --symbol fix_rule`
```
Index: cache-miss (283ms) | Query: 0ms | Total: 283ms
Impact: fix_rule (jangkau.py:107) def=107 span=107-175 [function]
Blast radius: 2 callers (1 direct, 1 transitive), 6 callees, 0 type consumers, 2 data flows, 2 co-change files, 0 siblings.
Callers (1 direct, 1 transitive; who breaks if behavior changes):
- run (jangkau.py:211, def :183)
- jangkau.py (jangkau.py) [via run]
Callees (6; what it depends on):
- shutil.copy
- audit (jangkau.py:50)
- visual_diff (jangkau.py:67)
- apply_edits (jangkau.py:77)
- parse_json (jangkau.py:88)
- log (jangkau.py:178)
Type consumers (0 in, 0 out; USES_TYPE/PARAM_TYPE/RETURNS_TYPE):
- none
Data flows (1 in, 1 out):
- -> audit (jangkau.py:50)
- <- run (jangkau.py:183)
Co-change coupling (2; files that historically change with jangkau.py):
- README.md [files changed together in 2 recent commits]
- test_jangkau.py [files changed together in 2 recent commits]
Same-container siblings (0):
- none
```

## `entire graph diff --base 963a4dd --head 4b332df` (v2 → v4 verifier changes)
```
Semantic changes 963a4dd..4b332df

BUSINESS.md (Markdown)
  - section Cost-per-page-estimate-replace-with-measured-value removed (0 dependents)
  + section Cost-per-page-measured added

demo_site/toko.html (HTML)
  + document toko added
  + element produk added
  + element ukuran added
  + element kontak added
  + element email added

hackathon.md (Markdown)
  ~ module hackathon.md body changed (0 dependents)

jangkau.py (Python)
  ~ function fix_rule signature changed (1 dependent)
  ~ function run body changed (1 dependent)

runs/dbg-toko-v1/index.html (HTML)
  + document index added
  + element menu added
  + element pesan added

runs/dbg-toko-v1/report.md (Markdown)
  + section Jangkau-report-v1-verify-False added

runs/dbg-toko-v1/state.json (JSON)
  + section target added
  + section version added
  + section verify added
  + section done added
  + section results added
  + section rule added
  + section status added
  + section attempts added
  + section baseline added
  + section nodes added
  + section by_rule added
  + section aria-hidden-focus added
  + section button-name added
  + section color-contrast added
  + section document-title added
  + section frame-title added
  + section heading-order added
  + section html-has-lang added
  + section image-alt added
  + section label added
  + section landmark-one-main added
  + section link-name added
  + section meta-viewport added
  + section page-has-heading-one added
  + section region added
  + section final added
  + section seconds added
  + section usage added
  + section prompt_tokens added
  + section completion_tokens added
  + section llm_calls added

runs/dbg-toko-v1/toko.html (HTML)
  + document toko added
  + element produk added
  + element ukuran added
  + element kontak added
  + element email added
  + element name added
  + element message added

runs/dbg-toko-v2/index.html (HTML)
  + document index added
  + element menu added
  + element pesan added

runs/dbg-toko-v2/report.md (Markdown)
  + section Jangkau-report-v2-verify-True added

runs/dbg-toko-v2/state.json (JSON)
  + section target added
  + section version added
  + section verify added
  + section done added
  + section results added
  + section rule added
  + section status added
  + section attempts added
  + section visual_diff added
  + section last_error added
  + section baseline added
  + section nodes added
  + section by_rule added
  + section aria-hidden-focus added
  + section button-name added
  + section color-contrast added
  + section document-title added
  + section frame-title added
  + section heading-order added
  + section html-has-lang added
  + section image-alt added
  + section label added
  + section landmark-one-main added
  + section link-name added
  + section meta-viewport added
  + section page-has-heading-one added
  + section region added
  + section final added
  + section seconds added
  + section usage added
  + section prompt_tokens added
  + section completion_tokens added
  + section llm_calls added

runs/dbg-toko-v2/toko.html (HTML)
  + document toko added
  + element produk added
  + element ukuran added
  + element kontak added
  + element email added

runs/dbg-toko-v3/index.html (HTML)
  + document index added
  + element menu added
  + element pesan added

runs/dbg-toko-v3/report.md (Markdown)
  + section Jangkau-report-v3-verify-True added

runs/dbg-toko-v3/state.json (JSON)
  + section target added
  + section version added
  + section verify added
  + section done added
  + section results added
  + section rule added
  + section status added
  + section attempts added
  + section last_feedback added
  + section baseline added
  + section nodes added
  + section by_rule added
  + section aria-hidden-focus added
  + section button-name added
  + section color-contrast added
  + section document-title added
  + section frame-title added
  + section heading-order added
  + section html-has-lang added
  + section image-alt added
  + section label added
  + section landmark-one-main added
  + section link-name added
  + section meta-viewport added
  + section page-has-heading-one added
  + section region added
  + section final added
  + section seconds added
  + section usage added
  + section prompt_tokens added
  + section completion_tokens added
  + section llm_calls added

runs/dbg-toko-v3/toko.html (HTML)
  + document toko added
  + element produk added
  + element ukuran added
  + element kontak added
  + element email added
  + element message added
  + element textarea-content added

runs/dbg-toko-v4/index.html (HTML)
  + document index added
  + element menu added
  + element pesan added

runs/dbg-toko-v4/report.md (Markdown)
  + section Jangkau-report-v4-verify-True added

runs/dbg-toko-v4/state.json (JSON)
  + section target added
  + section version added
  + section verify added
  + section done added
  + section results added
  + section rule added
  + section status added
  + section attempts added
  + section baseline added
  + section nodes added
  + section by_rule added
  + section aria-hidden-focus added
  + section button-name added
  + section color-contrast added
  + section document-title added
  + section frame-title added
  + section heading-order added
  + section html-has-lang added
  + section image-alt added
  + section label added
  + section landmark-one-main added
  + section link-name added
  + section meta-viewport added
  + section page-has-heading-one added
  + section region added
  + section final added
  + section seconds added
  + section usage added
  + section prompt_tokens added
  + section completion_tokens added
  + section llm_calls added

runs/dbg-toko-v4/toko.html (HTML)
  + document toko added
  + element produk added
  + element ukuran added
  + element kontak added
  + element email added
  + element message added
  + element textarea-content added

Warnings
  ! W_UNSUPPORTED_FILE demo_site/ig.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE demo_site/kopi-susu.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE demo_site/logo.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE demo_site/pisang.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE demo_site/v60.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/after.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/baseline.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/before.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/final.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/ig.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/kopi-susu.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/logo.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/pisang.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v1/v60.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/after.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/baseline.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/before.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/final.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/ig.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/kopi-susu.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/logo.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/pisang.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v2/v60.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/after.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/baseline.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/before.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/final.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/ig.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/kopi-susu.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/logo.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/pisang.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v3/v60.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/after.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/baseline.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/before.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/final.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/ig.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/kopi-susu.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/logo.png
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/pisang.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
  ! W_UNSUPPORTED_FILE runs/dbg-toko-v4/v60.jpg
    file skipped; no parser for this file type, so its changes are not analyzed
    head version has no supported parser
```
