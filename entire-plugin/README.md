# entire jangkau

An [Entire CLI](https://docs.entire.io) plugin that answers one question about an agent checkpoint:
**did it make the site less accessible?**

```
$ entire jangkau 01TESTREGRESSION0000000000
checkpoint 01TESTREGRESSION0000000000 -> commit cf267f6dbc99: 1 page(s) touched
  index.html: 18 -> 26 failing elements
    worse  html-has-lang: 0 -> 1
    worse  image-alt: 0 -> 7
verdict: REGRESSED (index.html)
```

`entire graph checkpoint <id>` shows which code a checkpoint changed. `entire jangkau <id>` shows what that change did
to the people using the page. The plugin:

1. Resolves the checkpoint id to its commit through the `Entire-Checkpoint` trailer. A plain commit works too.
2. Finds the HTML pages the commit touched, directly or through a stylesheet next to them.
3. Audits each page before and after the commit in a real browser, using Jangkau's axe-core audit (WCAG 2.x plus the
   custom F55 rule).
4. Prints the change per rule. It exits **1** if any page got worse, so a hook or CI job can block the checkpoint.

`--json` gives machine-readable output. It never calls a model and needs no API keys.

## Install

Entire discovers plugins as executables named `entire-<name>` on `PATH`. From the repo root, after the
[Jangkau setup](../README.md#run-it) (`.venv` with Playwright):

```bash
export PATH="$PATH:$(pwd)/entire-plugin"          # Windows: add entire-plugin\ to PATH (entire-jangkau.cmd)
entire jangkau <checkpoint-id> [--repo path] [--json]
```

Tested in `tests/test_e2e.py::test_entire_plugin_flags_a_checkpoint_that_regresses`.
