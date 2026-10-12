"""Measure what fixing a page really costs: full runs on real pages with each model, cost as reported
by the LiteLLM gateway. Writes runs/cost-bench/results.json and a markdown table.
Run from the repo root: python scripts/cost_bench.py <freelancer index.html>"""
import json
import os
import subprocess
import sys
from pathlib import Path

PAGES = {
    "batik shop (demo)": "demo_site/shop.html",
    "coffee shop (demo)": "demo_site/index.html",
    "StartBootstrap Freelancer": sys.argv[1],
    "W3C inaccessible demo (live)": "https://www.w3.org/WAI/demos/bad/before/home.html",
}
MODELS = ["claude-haiku", "claude-sonnet-4.6"]
OUT = Path("runs/cost-bench")

rows = []
for model in MODELS:
    for name, target in PAGES.items():
        out = OUT / f"{model}-{len(rows):02d}"
        env = {**os.environ, "JANGKAU_MODEL": model, "JANGKAU_VERSION": "v8-bench"}
        subprocess.run([sys.executable, "jangkau.py", target, "--out", str(out)], env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
        s = json.loads((out / "state.json").read_text(encoding="utf-8"))
        rows.append({"page": name, "model": model, "before": s["baseline"]["nodes"], "after": s["final"]["nodes"],
                     "llm_calls": s["usage"]["llm_calls"], "cost_usd": round(s["usage"]["cost_usd"], 4),
                     "by_model": s["usage"]["by_model"], "seconds": s["seconds"], "trace": s.get("trace_id")})
        print(json.dumps(rows[-1]), flush=True)

(OUT / "results.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
table = "\n".join(f"| {r['page']} | {r['model']} | {r['before']} → {r['after']} | {r['llm_calls']} | ${r['cost_usd']:.4f} | {r['seconds']}s |"
                  for r in rows)
(OUT / "README.md").write_text("| Page | Model | Failing nodes | LLM calls | Cost | Time |\n|---|---|---|---|---|---|\n"
                               + table + "\n", encoding="utf-8")
