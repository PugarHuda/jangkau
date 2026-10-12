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
        if v.strip():
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
from PIL import Image, ImageChops, ImageFilter  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from axe_playwright_python.sync_playwright import Axe  # noqa: E402

MODEL = os.getenv("JANGKAU_MODEL", "claude-sonnet-4.6")
ESCALATE_MODEL = os.getenv("JANGKAU_ESCALATE_MODEL", "claude-sonnet-4.6")  # last attempt on a stuck rule
IMPACT = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
MAX_ATTEMPTS = 3
# ponytail: one global threshold; per-rule thresholds if contrast fixes keep tripping it
VISUAL_LIMIT = 0.35
CONTENT_TAGS = "a,button,input,select,textarea,img,h1,h2,h3,label,li"
LANDMARKS = "main,nav,header,footer,aside,section,[role]"

llm = OpenAI(base_url=os.getenv("LITELLM_BASE_URL", "https://litellm.vision.aivar.app/v1"),
             api_key=os.getenv("LITELLM_API_KEY")
             or sys.exit("set LITELLM_API_KEY in .env (claim it at https://neatlogs.com/hackathon/models)"))
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
                    text: document.body.innerText.replace(/\\s+/g, ' ').trim().length,
                    emptyLandmarks: [...document.querySelectorAll({json.dumps(LANDMARKS)})]
                        .filter(e => !e.textContent.trim() && !e.querySelector({json.dumps(CONTENT_TAGS)})).length}})"""
    )
    return {
        "violations": violations,
        "nodes": sum(len(v["nodes"]) for v in violations),
        "by_rule": {v["id"]: len(v["nodes"]) for v in violations},
        "fingerprint": fingerprint,
    }


@span(kind="TOOL", name="visual_diff")
def visual_diff(a: Path, b: Path, layout: bool = False) -> float:
    """Share of pixels that changed noticeably, over the area both shots share.
    layout=True compares edge maps instead, so recolouring a section (the whole point of a
    contrast fix) passes while moved, hidden or overlapping elements still count."""
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    w, h = min(ia.width, ib.width), min(ia.height, ib.height)
    ia, ib = ia.crop((0, 0, w, h)), ib.crop((0, 0, w, h))
    if layout:
        ia, ib = (i.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 40 else 0)
                  for i in (ia, ib))
    diff = ImageChops.difference(ia, ib).convert("L")
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
def fix_rule(page, html: Path, work: Path, rule: dict, before: dict, verify: bool, done: list) -> dict:
    """Fix one rule. Accepted edits are kept and the rule is retried until it is fully
    resolved; rejected edits are rolled back. Returns fixed / partial / gave-up."""
    rid, start_nodes, feedback = rule["id"], len(rule["nodes"]), ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        source = html.read_text(encoding="utf-8")
        nodes = "\n".join(f"- target {n['target']}: {n['html'][:300]}\n  {n['failureSummary'][:300]}"
                          for n in rule["nodes"][:15])
        prompt = (f"Violation `{rid}` ({rule['impact']}): {rule['help']}\n{rule['helpUrl']}\n"
                  f"Failing nodes:\n{nodes}\n\nFile `{html.name}`:\n```html\n{source}\n```")
        if feedback:
            prompt += f"\n\nFeedback on your previous attempt: {feedback}"
        try:
            resp = llm.chat.completions.create(
                model=ESCALATE_MODEL if attempt == MAX_ATTEMPTS else MODEL, temperature=0,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
            usage["llm_calls"] += 1
            if resp.usage:
                usage["prompt_tokens"] += resp.usage.prompt_tokens
                usage["completion_tokens"] += resp.usage.completion_tokens
            plan = parse_json(resp.choices[0].message.content or "")
            html.write_text(apply_edits(source, plan.get("edits", [])), encoding="utf-8", newline="\n")
        except Exception as e:  # bad JSON, non-unique find, API hiccup -> retry with feedback
            feedback = f"it failed with {type(e).__name__}: {e}. Try again."
            log(f"  attempt {attempt} failed before audit: {e}")
            continue

        after = audit(page, html, work / "after.png")
        if not verify:
            return {"rule": rid, "status": "applied-unverified", "attempts": attempt}

        left = after["by_rule"].get(rid, 0)
        problems = []
        if left >= before["by_rule"].get(rid, 0):
            still = next((v for v in after["violations"] if v["id"] == rid), {"nodes": []})
            measured = " | ".join(f"{n['html'][:150]} ({n['failureSummary'][-250:]})" for n in still["nodes"][:5])
            problems.append(f"`{rid}` still has {left} failing nodes after your edit. Measured on the "
                            f"rendered page: {measured}. Check inherited styles (opacity, overlays, "
                            f"text-shadow) that change the rendered colour")
        # Rules still waiting in the queue may grow (e.g. a new <label> outside a landmark
        # adds a `region` node); they get fixed later. Regressions in finished rules or
        # brand-new rules are real breakage.
        new = {k: v for k, v in after["by_rule"].items()
               if v > before["by_rule"].get(k, 0) and (k in done or k not in before["by_rule"])}
        if new:
            detail = " | ".join(f"{v['id']}: {v['help']} at {v['nodes'][0]['html'][:150]} "
                                f"({v['nodes'][0]['failureSummary'][:200]})"
                                for v in after["violations"] if v["id"] in new)
            problems.append(f"the edit introduced new violations {new}: {detail}")
        fb, fa = before["fingerprint"], after["fingerprint"]
        if fa["elements"] < fb["elements"] or fa["text"] < fb["text"] * 0.95:
            problems.append(f"content was removed (elements {fb['elements']}->{fa['elements']}, "
                            f"text {fb['text']}->{fa['text']} chars); fix it without deleting anything")
        if fa["emptyLandmarks"] > fb["emptyLandmarks"]:
            problems.append("the edit added an empty landmark; a landmark must wrap the existing "
                            "content it describes, so move that content inside it")
        vd = visual_diff(work / "before.png", work / "after.png", layout=rid == "color-contrast")
        if vd > VISUAL_LIMIT:
            what = "the layout shifted" if rid == "color-contrast" else "the page changed visually too much"
            problems.append(f"{what} ({vd:.0%} of pixels)")

        if problems:
            feedback = "it was rejected and rolled back: " + "; ".join(problems) + ". Try a different fix."
            log(f"  attempt {attempt} rejected, reverting: {'; '.join(problems)}")
            html.write_text(source, encoding="utf-8", newline="\n")  # recovery: roll back the bad edit
            continue
        if left == 0:
            return {"rule": rid, "status": "fixed", "attempts": attempt}
        # partial progress: keep the edit, retry the remaining nodes
        log(f"  attempt {attempt} accepted, {left} nodes left")
        before = after
        shutil.copy(work / "after.png", work / "before.png")
        rule = next(v for v in after["violations"] if v["id"] == rid)
        feedback = f"it was accepted, but {left} nodes still fail (listed above). Fix those too."
    left = before["by_rule"].get(rid, 0)
    return {"rule": rid, "status": "partial" if left < start_nodes else "gave-up",
            "attempts": MAX_ATTEMPTS, "last_feedback": feedback}


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
    headers = {}
    neatlogs.inject_trace_context(headers)  # traceparent = 00-<trace id>-<span id>-01
    state["trace_id"] = headers.get("traceparent", "-").split("-")[1] if headers else "-"
    log(f"neatlogs trace: {state['trace_id']}")

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
            result = fix_rule(page, html, out, rule, current, verify, state["done"])
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
neatlogs trace: `{s.get('trace_id', '-')}`

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


@span(kind="TOOL", name="open_pr")
def open_pr(target: Path, out: Path):
    """Commit the fixed page on a new branch in the target's repo and open a PR with the report."""
    import subprocess
    repo, name = target.resolve().parent, target.name
    git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
    branch = f"jangkau/{target.stem}-{time.strftime('%Y%m%d-%H%M%S')}"
    base = git("rev-parse", "--abbrev-ref", "HEAD")
    git("switch", "-c", branch)
    try:
        shutil.copy(out / name, repo / name)
        git("add", name)
        git("commit", "-m", f"Fix WCAG violations in {name} (Jangkau)")
        git("push", "-u", "origin", branch)
        url = subprocess.run(["gh", "pr", "create", "--base", base, "--head", branch,
                              "--title", f"Accessibility fixes for {name}", "--body-file", str((out / "report.md").resolve())],
                             cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
        log(f"pull request: {url}")
    finally:
        git("switch", base)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Fix WCAG violations in an HTML page and prove each fix.")
    ap.add_argument("target", type=Path, help="path to the HTML file to fix")
    ap.add_argument("--out", type=Path, default=Path("runs") / time.strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--no-verify", action="store_true", help="baseline mode: accept edits without checks")
    ap.add_argument("--pr", action="store_true", help="write the fix back into the target's git repo and open a PR")
    a = ap.parse_args()
    if not a.target.exists():
        sys.exit(f"not found: {a.target}")
    s = run(a.target, a.out, verify=not a.no_verify)
    log(f"done: {s['baseline']['nodes']} -> {s['final']['nodes']} failing nodes. report: {a.out / 'report.md'}")
    if a.pr and s["final"]["nodes"] < s["baseline"]["nodes"]:
        open_pr(a.target, a.out)
    neatlogs.flush()
    neatlogs.shutdown()
