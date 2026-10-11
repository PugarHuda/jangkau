"""Jangkau: an agent that audits a web page for WCAG issues, patches the HTML,
and proves every fix with a re-audit, a visual diff and a content guard."""
import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

for line in Path(".env").read_text().splitlines() if Path(".env").exists() else []:
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

import neatlogs  # must init before importing openai so calls get traced

VERSION = os.getenv("JANGKAU_VERSION", "v2")
neatlogs.init(
    workflow_name="jangkau",
    tags=[f"version:{VERSION}"],
    instrumentations=["openai"],
    disable_export=not os.getenv("NEATLOGS_API_KEY"),
)
from neatlogs import span  # noqa: E402
from openai import OpenAI  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from axe_playwright_python.sync_playwright import Axe  # noqa: E402

MODEL = os.getenv("JANGKAU_MODEL", "claude-sonnet")
IMPACT = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
MAX_ATTEMPTS = 3
# ponytail: one global threshold; per-rule thresholds if contrast fixes keep tripping it
VISUAL_LIMIT = 0.35
CONTENT_TAGS = "a,button,input,select,textarea,img,h1,h2,h3,label,li"

llm = OpenAI()  # reads OPENAI_BASE_URL / OPENAI_API_KEY (the LiteLLM proxy)
axe = Axe()
usage = {"prompt_tokens": 0, "completion_tokens": 0, "llm_calls": 0}


# ---------- tools ----------

@span(kind="TOOL", name="audit")
def audit(page, html_path: Path, shot: Path) -> dict:
    page.goto(html_path.resolve().as_uri())
    page.screenshot(path=str(shot), full_page=True)
    violations = axe.run(page).response["violations"]
    fingerprint = page.evaluate(
        f"""() => ({{elements: document.querySelectorAll({json.dumps(CONTENT_TAGS)}).length,
                    text: document.body.innerText.replace(/\\s+/g, ' ').trim().length}})"""
    )
    return {
        "violations": violations,
        "nodes": sum(len(v["nodes"]) for v in violations),
        "by_rule": {v["id"]: len(v["nodes"]) for v in violations},
        "fingerprint": fingerprint,
    }


@span(kind="TOOL", name="visual_diff")
def visual_diff(a: Path, b: Path) -> float:
    """Share of pixels that changed noticeably, over the area both shots share."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    w, h = min(ia.width, ib.width), min(ia.height, ib.height)
    diff = ImageChops.difference(ia.crop((0, 0, w, h)), ib.crop((0, 0, w, h))).convert("L")
    changed = sum(diff.point(lambda p: 255 if p > 40 else 0).histogram()[255:])
    return changed / (w * h)


@span(kind="TOOL", name="apply_edits")
def apply_edits(source: str, edits: list) -> str:
    """Apply find/replace edits; each `find` must match exactly once."""
    for i, e in enumerate(edits):
        find, repl = e.get("find", ""), e.get("replace", "")
        n = source.count(find) if find else 0
        if n != 1:
            raise ValueError(f"edit {i}: `find` matched {n} times (must be exactly 1): {find[:80]!r}")
        source = source.replace(find, repl, 1)
    return source


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("model reply contained no JSON object")
    return json.loads(m.group(0))


# ---------- agent ----------

SYSTEM = """You fix WCAG accessibility violations in an HTML file.
Return ONLY JSON: {"reasoning": "...", "edits": [{"find": "<exact substring of the file>", "replace": "<new text>"}]}
Rules:
- `find` must be copied verbatim from the file and occur exactly once. Keep it short but unique.
- Fix the root cause (add labels, alt text, lang, roles, contrast colors in CSS...).
- NEVER delete content, links, buttons, inputs or images to make a violation disappear.
- Keep the visual design as close to the original as possible."""


@span(kind="AGENT", name="fix_rule")
def fix_rule(page, html: Path, work: Path, rule: dict, before: dict, verify: bool) -> dict:
    feedback = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        source = html.read_text(encoding="utf-8")
        nodes = "\n".join(f"- target {n['target']}: {n['html'][:300]}\n  {n['failureSummary'][:300]}"
                          for n in rule["nodes"][:15])
        prompt = (f"Violation `{rule['id']}` ({rule['impact']}): {rule['help']}\n{rule['helpUrl']}\n"
                  f"Failing nodes:\n{nodes}\n\nFile `{html.name}`:\n```html\n{source}\n```")
        if feedback:
            prompt += f"\n\nYour previous attempt was rejected: {feedback}\nTry a different fix."
        try:
            resp = llm.chat.completions.create(
                model=MODEL, temperature=0,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
            usage["llm_calls"] += 1
            if resp.usage:
                usage["prompt_tokens"] += resp.usage.prompt_tokens
                usage["completion_tokens"] += resp.usage.completion_tokens
            plan = parse_json(resp.choices[0].message.content or "")
            html.write_text(apply_edits(source, plan.get("edits", [])), encoding="utf-8")
        except Exception as e:  # bad JSON, non-unique find, API hiccup -> retry with feedback
            feedback = f"{type(e).__name__}: {e}"
            log(f"  attempt {attempt} failed before audit: {feedback}")
            continue

        after = audit(page, html, work / "after.png")
        if not verify:
            return {"rule": rule["id"], "status": "applied-unverified", "attempts": attempt, "after": after}

        problems = []
        if after["by_rule"].get(rule["id"], 0) >= before["by_rule"].get(rule["id"], 0):
            problems.append(f"`{rule['id']}` still has {after['by_rule'].get(rule['id'], 0)} failing nodes")
        new = {k: v for k, v in after["by_rule"].items() if v > before["by_rule"].get(k, 0)}
        if new:
            problems.append(f"the edit introduced new violations: {new}")
        fb, fa = before["fingerprint"], after["fingerprint"]
        if fa["elements"] < fb["elements"] or fa["text"] < fb["text"] * 0.95:
            problems.append(f"content was removed (elements {fb['elements']}->{fa['elements']}, "
                            f"text {fb['text']}->{fa['text']} chars); fix it without deleting anything")
        vd = visual_diff(work / "before.png", work / "after.png")
        if vd > VISUAL_LIMIT:
            problems.append(f"the page changed visually too much ({vd:.0%} of pixels)")

        if not problems:
            return {"rule": rule["id"], "status": "fixed", "attempts": attempt,
                    "visual_diff": round(vd, 3), "after": after}
        feedback = "; ".join(problems)
        log(f"  attempt {attempt} rejected, reverting: {feedback}")
        html.write_text(source, encoding="utf-8")  # recovery: roll back the bad edit
    return {"rule": rule["id"], "status": "gave-up", "attempts": MAX_ATTEMPTS, "last_error": feedback}


def log(msg: str):
    print(msg, flush=True)


@span(kind="WORKFLOW", name="jangkau_run")
def run(target: Path, out: Path, verify: bool) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    state_file = out / "state.json"
    html = out / target.name
    if state_file.exists():  # resume an interrupted run
        state = json.loads(state_file.read_text())
        log(f"resuming run: {len(state['done'])} rules already handled")
    else:
        shutil.copytree(target.parent, out, dirs_exist_ok=True)
        state = {"target": str(target), "version": VERSION, "verify": verify, "done": [], "results": []}

    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page(viewport={"width": 1280, "height": 800})
        start = time.time()
        if "baseline" not in state:
            base = audit(page, html, out / "baseline.png")
            state["baseline"] = {"nodes": base["nodes"], "by_rule": base["by_rule"]}
        log(f"baseline: {state['baseline']['nodes']} failing nodes across "
            f"{len(state['baseline']['by_rule'])} rules")

        while True:
            current = audit(page, html, out / "before.png")
            todo = sorted((v for v in current["violations"] if v["id"] not in state["done"]),
                          key=lambda v: IMPACT.get(v["impact"], 9))
            if not todo:
                break
            rule = todo[0]
            log(f"fixing {rule['id']} ({rule['impact']}, {len(rule['nodes'])} nodes)")
            result = fix_rule(page, html, out, rule, current, verify)
            result.pop("after", None)
            log(f"  -> {result['status']} after {result['attempts']} attempt(s)")
            state["done"].append(rule["id"])
            state["results"].append(result)
            state_file.write_text(json.dumps(state, indent=2))

        final = audit(page, html, out / "final.png")
        state["final"] = {"nodes": final["nodes"], "by_rule": final["by_rule"]}
        state["seconds"] = round(time.time() - start, 1)
        state["usage"] = usage
        state_file.write_text(json.dumps(state, indent=2))
    write_report(state, out / "report.md")
    return state


def write_report(s: dict, path: Path):
    b, f = s["baseline"]["nodes"], s["final"]["nodes"]
    rows = "\n".join(f"| `{r['rule']}` | {r['status']} | {r['attempts']} | "
                     f"{s['baseline']['by_rule'].get(r['rule'], 0)} → {s['final']['by_rule'].get(r['rule'], 0)} |"
                     for r in s["results"])
    path.write_text(f"""# Jangkau report ({s['version']}, verify={s['verify']})

Target: `{s['target']}`

| Metric | Value |
|---|---|
| Failing nodes before | {b} |
| Failing nodes after | {f} |
| Reduction | {(b - f) / b:.0%} |
| LLM calls | {s['usage']['llm_calls']} |
| Tokens (in/out) | {s['usage']['prompt_tokens']} / {s['usage']['completion_tokens']} |
| Wall time | {s['seconds']}s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
{rows}
""" if b else "# Jangkau report\n\nNo violations found.\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fix WCAG violations in an HTML page and prove each fix.")
    ap.add_argument("target", type=Path, help="path to the HTML file to fix")
    ap.add_argument("--out", type=Path, default=Path("runs") / time.strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--no-verify", action="store_true", help="baseline mode: accept edits without checks")
    a = ap.parse_args()
    if not a.target.exists():
        sys.exit(f"not found: {a.target}")
    s = run(a.target, a.out, verify=not a.no_verify)
    log(f"done: {s['baseline']['nodes']} -> {s['final']['nodes']} failing nodes. report: {a.out / 'report.md'}")
    neatlogs.flush()
    neatlogs.shutdown()
