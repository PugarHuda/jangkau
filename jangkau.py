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

VERSION = os.getenv("JANGKAU_VERSION", "v5")


def slim_axe(value):
    """Drop axe's bulky per-check detail (tags, any/all/none, relatedNodes, descriptions) and keep
    what a reader of the trace needs: rule, impact, failing element and why it fails."""
    if isinstance(value, dict):
        out = {k: slim_axe(v) for k, v in value.items()
               if k not in ("tags", "any", "all", "none", "relatedNodes", "description", "helpUrl")}
        if "html" in out and isinstance(out["html"], str):
            out["html"] = out["html"][:200]
        return out
    if isinstance(value, list):
        return [slim_axe(v) for v in value]
    return value


def slim_span(span: dict) -> dict:
    """neatlogs mask: an audit returns ~30 KB of axe JSON per call; keep the parts that explain
    a decision. Applied at export, so the agent still sees the full result."""
    for key, val in list((span.get("attributes") or {}).items()):
        if isinstance(val, str) and len(val) > 2000 and '"violations"' in val:
            try:
                span["attributes"][key] = json.dumps(slim_axe(json.loads(val)))
            except ValueError:
                pass
    return span


neatlogs.init(
    workflow_name="jangkau",
    tags=[f"version:{VERSION}"],
    instrumentations=["openai"],
    disable_export=not os.getenv("NEATLOGS_API_KEY"),
    mask=slim_span,
)
from neatlogs import span  # noqa: E402
from opentelemetry import trace as otel_trace  # noqa: E402
from openai import OpenAI  # noqa: E402
from PIL import Image, ImageChops, ImageFilter  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from axe_playwright_python.sync_playwright import Axe  # noqa: E402

MODEL = os.getenv("JANGKAU_MODEL", "claude-sonnet-4.6")
ESCALATE_MODEL = os.getenv("JANGKAU_ESCALATE_MODEL", "claude-sonnet-4.6")  # last attempt on a stuck rule
IMPACT = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
MAX_ATTEMPTS = 3        # attempts per rule while stuck
MAX_ATTEMPTS_PROGRESS = 8  # hard cap: every accepted partial fix earns one more attempt
# ponytail: one global threshold; per-rule thresholds if contrast fixes keep tripping it
VISUAL_LIMIT = 0.35
CONTENT_TAGS = "a,button,input,select,textarea,img,h1,h2,h3,label,li"
LANDMARKS = "main,nav,header,footer,aside,section,[role]"
SETTLE_MS = 0  # --wait: let intro animations finish before auditing

_llm = None


def llm() -> OpenAI:
    """Created on first use, so audit-only runs (CI, no secrets) never need a model key."""
    global _llm
    if _llm is None:
        _llm = OpenAI(base_url=os.getenv("LITELLM_BASE_URL", "https://litellm.vision.aivar.app/v1"),
                      api_key=os.getenv("LITELLM_API_KEY")
                      or sys.exit("set LITELLM_API_KEY in .env (claim it at https://neatlogs.com/hackathon/models)"))
    return _llm


axe = Axe()
# A rule axe-core lacks, found on W3C's demo page: onfocus="blur()" throws keyboard focus away, so
# keyboard users can never act on the element (WCAG failure F55; 2.1.1 and 2.4.7). Neither axe nor
# HTML_CodeSniffer flags it.
axe.axe_script += r"""
;axe.configure({
  checks: [{id: 'focus-not-removed', evaluate: function (node) {
      return !/\bblur\s*\(/.test(node.getAttribute('onfocus') || ''); },
    metadata: {impact: 'serious', messages: {pass: 'Focus stays on the element',
      fail: 'onfocus calls blur(), which removes keyboard focus as soon as the element receives it'}}}],
  rules: [{id: 'focus-not-removed', selector: '[onfocus]', any: ['focus-not-removed'], impact: 'serious',
    tags: ['cat.keyboard', 'wcag2a', 'wcag211', 'wcag2aa', 'wcag247', 'EN-301-549', 'EN-9.2.1.1', 'EN-9.2.4.7'],
    metadata: {description: 'Ensure elements do not remove keyboard focus when they receive it',
      help: 'Elements must not remove focus when focused (WCAG failure F55)',
      helpUrl: 'https://www.w3.org/WAI/WCAG22/Techniques/failures/F55'}}]
});"""
HTMLCS_JS = (Path(__file__).parent / "vendor" / "HTMLCS.js").read_text(encoding="utf-8")


@span(kind="TOOL", name="crosscheck_htmlcs")
def crosscheck(page) -> dict:
    """Second, independent engine on the page that is loaded: HTML_CodeSniffer (WCAG2AA), the engine
    behind Pa11y. Reported next to axe, not used as a gate: its technique-level checks sometimes
    disagree with a valid fix (e.g. alt="" inside a link that has an aria-label)."""
    page.add_script_tag(content=HTMLCS_JS)
    items = page.evaluate("""() => new Promise(done => HTMLCS.process('WCAG2AA', document, () => done(
        HTMLCS.getMessages().filter(m => m.type === 1).map(m => ({
            code: m.code.split('.').slice(3, 5).join('.'), msg: m.msg.slice(0, 200),
            html: (m.element.outerHTML || '').slice(0, 160)})))))""")
    return {"errors": len(items), "items": items}
usage = {"prompt_tokens": 0, "completion_tokens": 0, "llm_calls": 0, "cost_usd": 0.0, "by_model": {}}
MAX_COST = None  # --max-cost: stop starting new rules once a page has cost this much (USD)


# ---------- tools ----------

@span(kind="TOOL", name="audit")
def audit(page, html_path: Path, shot: Path) -> dict:
    page.goto(html_path.resolve().as_uri())
    if SETTLE_MS:
        page.wait_for_timeout(SETTLE_MS)
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
    with Image.open(a) as fa, Image.open(b) as fb:  # close the files: Windows can't overwrite open ones
        ia, ib = fa.convert("RGB"), fb.convert("RGB")
    w, h = min(ia.width, ib.width), min(ia.height, ib.height)
    ia, ib = ia.crop((0, 0, w, h)), ib.crop((0, 0, w, h))
    if layout:
        ia, ib = (i.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda p: 255 if p > 40 else 0)
                  for i in (ia, ib))
    diff = ImageChops.difference(ia, ib).convert("L")
    changed = sum(diff.point(lambda p: 255 if p > 40 else 0).histogram()[255:])
    return changed / (w * h)


@span(kind="TOOL", name="apply_edits")
def apply_valid_edits(source: str, edits: list) -> tuple:
    """Apply each find/replace whose `find` matches exactly once; collect the rest as errors.
    One mistyped `find` in a batch of 20 alt-text edits no longer throws away the other 19:
    the re-audit judges what was applied, and the skipped edits go back to the model."""
    errors = []
    for i, e in enumerate(edits):
        find, repl = e.get("find", ""), e.get("replace", "")
        n = source.count(find) if find else 0
        if n != 1:
            errors.append(f"edit {i}: `find` matched {n} times (must be exactly 1): {find[:80]!r}")
            continue
        source = source.replace(find, repl, 1)
    return source, errors


def apply_edits(source: str, edits: list) -> str:
    """Strict variant: every `find` must match exactly once."""
    source, errors = apply_valid_edits(source, edits)
    if errors:
        raise ValueError(errors[0])
    return source


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("model reply contained no JSON object")
    return json.loads(m.group(0))


# ---------- standards and reporting ----------

LEVELS = {"wcag2a": "A", "wcag21a": "A", "wcag22a": "A", "wcag2aa": "AA", "wcag21aa": "AA",
          "wcag22aa": "AA", "wcag2aaa": "AAA", "best-practice": "best practice"}
SARIF_LEVEL = {"critical": "error", "serious": "error", "moderate": "warning", "minor": "note"}


def standards(tags: list) -> dict:
    """axe tags -> WCAG success criteria, conformance level and EN 301 549 clauses (the standard
    the European Accessibility Act points to). 'wcag1410' is SC 1.4.10, 'EN-9.1.4.3' is clause 9.1.4.3."""
    sc = sorted({f"{t[4]}.{t[5]}.{t[6:]}" for t in tags if re.fullmatch(r"wcag\d{3,4}", t)})
    en = sorted({t[3:] for t in tags if re.fullmatch(r"EN-\d+(\.\d+)+", t)})
    level = next((LEVELS[t] for t in tags if t in LEVELS), "")
    return {"wcag": sc, "level": level, "en301549": en}


def find_line(source: str, snippet: str, nth: int = 0) -> int:
    """1-based line of the nth occurrence of an element in the source: try its opening tag, then
    shorter prefixes, since the browser re-serialises attributes. Line 1 for document-level rules."""
    tag = snippet.split(">")[0]
    m = re.match(r"<[\w-]+", tag)
    if not m:
        return 1
    attrs = re.findall(r'\s+[^\s=>]+(?:="[^"]*")?', tag[m.end():])
    # browsers add or reorder attributes (style="", re-quoted values): fall back to fewer of them
    probes = [re.escape(tag + ">")] + [re.escape(m.group(0) + "".join(attrs[:k])) + r"(?=[\s/>])"
                                       for k in range(len(attrs), -1, -1)]
    for probe in probes:
        hits = [m.start() for m in re.finditer(probe, source)]
        if hits:
            return source.count("\n", 0, hits[min(nth, len(hits) - 1)]) + 1
    return 1


def to_sarif(violations: list, source: str, uri: str) -> dict:
    """SARIF 2.1.0, the format GitHub code scanning ingests: one rule per axe rule, one result per
    failing element, with the WCAG / EN 301 549 mapping in properties."""
    rules, results, seen = [], [], {}
    for v in violations:
        std = standards(v.get("tags", []))
        rules.append({
            "id": v["id"], "name": v["id"], "shortDescription": {"text": v["help"]},
            "fullDescription": {"text": v.get("description", v["help"])}, "helpUri": v.get("helpUrl"),
            "help": {"text": f"{v['help']}. WCAG {', '.join(std['wcag']) or '-'} ({std['level'] or '-'}); "
                             f"EN 301 549 {', '.join(std['en301549']) or '-'}."},
            "properties": {"tags": ["accessibility"] + std["wcag"], **std},
        })
        for n in v["nodes"]:
            key = (v["id"], n["html"].split(">")[0])
            seen[key] = nth = seen.get(key, -1) + 1
            results.append({
                "ruleId": v["id"], "level": SARIF_LEVEL.get(v["impact"], "warning"),
                "message": {"text": f"{v['help']}: {n['html'][:200]}. {n['failureSummary'][:300]}"},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": uri},
                    "region": {"startLine": find_line(source, n["html"], nth)}}}],
                "partialFingerprints": {"target": "|".join(map(str, n["target"]))},
            })
    return {"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
            "runs": [{"tool": {"driver": {"name": "Jangkau", "informationUri": "https://github.com/PugarHuda/jangkau",
                                          "rules": rules}},
                      "results": results}]}


def new_page(pw):
    """One browser page for every audit, snapshot and crawl. With VERCEL_AUTOMATION_BYPASS_SECRET set,
    every request carries Vercel's protection-bypass header, so protected preview deployments can be
    audited from CI (Vercel: Deployment Protection > Protection Bypass for Automation)."""
    headers = {}
    if os.getenv("VERCEL_AUTOMATION_BYPASS_SECRET"):
        headers = {"x-vercel-protection-bypass": os.environ["VERCEL_AUTOMATION_BYPASS_SECRET"],
                   "x-vercel-set-bypass-cookie": "true"}
    return pw.chromium.launch().new_context(viewport={"width": 1280, "height": 800},
                                            extra_http_headers=headers).new_page()


@span(kind="TOOL", name="snapshot_url")
def snapshot_url(url: str, out: Path) -> Path:
    """Save a live page as HTML with <base href> so its CSS, images and scripts still load from
    the original site. The agent then works on the saved copy."""
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        page = new_page(pw)
        page.goto(url, wait_until="networkidle", timeout=60000)
        html, final_url = page.content(), page.url
    base = f'<base href="{final_url}">'
    if re.search(r"<head", html, re.I):
        html = re.sub(r"<head([^>]*)>", lambda m: f"<head{m.group(1)}>{base}", html, count=1, flags=re.I)
    else:
        html = base + html
    target = out / "index.html"
    target.write_text(html, encoding="utf-8", newline="\n")
    return target


NOT_PAGES = re.compile(r"\.(png|jpe?g|gif|svg|webp|ico|pdf|zip|css|js|json|xml|txt|mp4|webm|woff2?)$", re.I)


@span(kind="TOOL", name="discover_pages")
def discover_pages(start: str, limit: int) -> list:
    """HTML pages reachable from `start`, breadth first, at most `limit`, staying on the same host and
    under the start URL's directory (crawling /docs/intro.html covers /docs/, not the whole site)."""
    from urllib.parse import urldefrag, urlparse
    origin = urlparse(start).netloc
    scope = urlparse(start).path.rsplit("/", 1)[0] + "/"
    queue, seen, pages = [urldefrag(start)[0]], {urldefrag(start)[0]}, []
    with sync_playwright() as pw:
        page = new_page(pw)
        while queue and len(pages) < limit:
            url = queue.pop(0)
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                log(f"  skip {url}: {type(e).__name__}")
                continue
            if not resp or resp.status >= 400 or "html" not in resp.headers.get("content-type", ""):
                continue
            if page.url not in pages:
                pages.append(page.url)
            for href in page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)"):
                u = urldefrag(href)[0]
                p = urlparse(u)
                if p.scheme in ("http", "https") and p.netloc == origin and p.path.startswith(scope) and u not in seen and not NOT_PAGES.search(p.path):
                    seen.add(u)
                    queue.append(u)
    return pages


@span(kind="WORKFLOW", name="jangkau_site_audit")
def audit_site(start: str, limit: int, out: Path, sarif: "Path | None") -> dict:
    """Crawl a site and audit every page: one report for the site, one SARIF with page URLs."""
    pages = discover_pages(start, limit)
    log(f"crawl: {len(pages)} page(s) from {start}")
    results, rules, all_results = [], {}, []
    for i, url in enumerate(pages, 1):
        d = out / "pages" / f"{i:02d}"
        s = audit_only(snapshot_url(url, d / "source"), d, d / "page.sarif" if sarif else None)
        results.append({"url": url, "dir": f"pages/{i:02d}", "nodes": s["baseline"]["nodes"],
                        "rules": len(s["baseline"]["by_rule"]), "htmlcs": s["crosscheck"]["before"]["errors"]})
        for v in s["violations"]:
            r = rules.setdefault(v["id"], {"id": v["id"], "impact": v["impact"], "tags": v.get("tags", []),
                                          "help": v["help"], "pages": 0, "nodes": 0})
            r["pages"] += 1
            r["nodes"] += len(v["nodes"])
        if sarif:
            run_ = json.loads((d / "page.sarif").read_text(encoding="utf-8"))["runs"][0]
            for res in run_["results"]:
                res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] = url
            all_results.append(run_)
        log(f"  {url}: {s['baseline']['nodes']} failing elements")
    top = sorted(rules.values(), key=lambda r: (IMPACT.get(r["impact"], 9), -r["pages"], -r["nodes"]))
    rows = "\n".join(f"| [{r['url']}]({r['url']}) | {r['nodes']} | {r['rules']} | {r['htmlcs']} | [report]({r['dir']}/report.md) |"
                     for r in results)
    rule_rows = "\n".join(f"| `{r['id']}` | {r['impact']} | {', '.join(standards(r['tags'])['wcag']) or '-'} | "
                          f"{', '.join(standards(r['tags'])['en301549']) or '-'} | {r['pages']}/{len(results)} | {r['nodes']} |"
                          for r in top)
    (out / "report.md").write_text(f"""# Jangkau site audit ({VERSION})

Start: {start}
Pages audited: **{len(results)}**, failing elements: **{sum(r['nodes'] for r in results)}**

| Page | axe failing elements | Rules | HTML_CodeSniffer errors | Details |
|---|---|---|---|---|
{rows}

## Rules across the site

| Rule | Impact | WCAG SC | EN 301 549 | Pages | Elements |
|---|---|---|---|---|---|
{rule_rows}
""", encoding="utf-8")
    if sarif:
        merged = all_results[0] if all_results else {"tool": {"driver": {"name": "Jangkau", "rules": []}}, "results": []}
        seen_rules = {r["id"] for r in merged["tool"]["driver"]["rules"]}
        for r_ in all_results[1:]:
            merged["tool"]["driver"]["rules"] += [r for r in r_["tool"]["driver"]["rules"] if r["id"] not in seen_rules]
            seen_rules |= {r["id"] for r in r_["tool"]["driver"]["rules"]}
            merged["results"] += r_["results"]
        sarif.parent.mkdir(parents=True, exist_ok=True)
        sarif.write_text(json.dumps({"$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
                                     "runs": [merged]}, indent=2), encoding="utf-8")
    return {"pages": results, "rules": top,
            "violations": [{"id": r["id"], "impact": r["impact"]} for r in top]}


@span(kind="WORKFLOW", name="jangkau_audit")
def audit_only(target: Path, out: Path, sarif: "Path | None") -> dict:
    """Audit without fixing: no model key needed. Writes report.md and, optionally, SARIF."""
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        page = new_page(pw)
        res = audit(page, target, out / "audit.png")
        cross = crosscheck(page)
    s = {"target": str(target), "version": VERSION, "verify": "audit-only", "results": [],
         "baseline": {"nodes": res["nodes"], "by_rule": res["by_rule"]},
         "final": {"nodes": res["nodes"], "by_rule": res["by_rule"]}, "violations": res["violations"],
         "crosscheck": {"before": cross}}
    write_report(s, out / "report.md")
    if sarif:
        uri = os.path.relpath(target.resolve(), Path.cwd()).replace(os.sep, "/")
        source = target.read_text(encoding="utf-8", errors="replace")
        sarif.parent.mkdir(parents=True, exist_ok=True)
        sarif.write_text(json.dumps(to_sarif(res["violations"], source, uri), indent=2), encoding="utf-8")
    return s


# ---------- agent ----------

SYSTEM = """You fix WCAG accessibility violations in an HTML file.
Return ONLY JSON: {"reasoning": "...", "edits": [{"find": "<exact substring of the file>", "replace": "<new text>"}]}
Rules:
- `find` must be copied verbatim from the file and occur exactly once. Keep it short but unique.
- Fix the root cause (add labels, alt text, lang, roles, contrast colors in CSS...).
- NEVER delete content, links, buttons, inputs or images to make a violation disappear.
- Keep the visual design as close to the original as possible."""

# The system prompt lives in the neatlogs prompt registry, so a prompt change is versioned and every
# trace records which version ran. SYSTEM above is the fallback when the registry can't be reached.
PROMPT_NAME = "jangkau-fixer-system"
PROMPT = {"content": SYSTEM, "ref": "local"}


def load_prompt() -> dict:
    if not os.getenv("NEATLOGS_API_KEY"):
        return {"content": SYSTEM, "ref": "local"}
    label = os.getenv("JANGKAU_PROMPT_LABEL", "production")
    try:
        h = neatlogs.get_prompt(PROMPT_NAME, label=label)
        return {"content": h.content, "ref": f"{PROMPT_NAME}@v{h.version} ({label})"}
    except Exception as e:  # registry down or prompt missing: run with the local copy, and say so
        log(f"prompt registry unavailable ({type(e).__name__}), using the local system prompt")
        return {"content": SYSTEM, "ref": "local (registry unavailable)"}


def sync_prompt(label: str) -> str:
    """Push the local SYSTEM to the registry as a new version under `label`, if it changed."""
    try:
        h = neatlogs.get_prompt(PROMPT_NAME, label=label)
    except Exception:
        h = None
    if h and h.content == SYSTEM:
        return f"{PROMPT_NAME}@v{h.version} ({label}) already matches the local prompt"
    if h is None:
        h = neatlogs.create_prompt(name=PROMPT_NAME, prompt=SYSTEM, labels=[label], config={"temperature": 0},
                                   commit_message="System prompt of the fixing agent")
        return f"created {PROMPT_NAME}@v{h.version} ({label})"
    v = neatlogs.save_as_version(prompt_name=PROMPT_NAME, content=SYSTEM, labels=[label],
                                 commit_message=f"Sync from jangkau.py ({VERSION})")
    return f"saved {PROMPT_NAME} version {v.get('version', '?')} ({label})"


@span(kind="AGENT", name="fix_rule")
def fix_rule(page, html: Path, work: Path, rule: dict, before: dict, verify: bool, done: list) -> dict:
    """Fix one rule. Accepted edits are kept and the rule is retried until it is fully
    resolved; rejected edits are rolled back. Returns fixed / partial / gave-up."""
    rid, start_nodes, feedback = rule["id"], len(rule["nodes"]), ""
    budget, stuck, attempt = MAX_ATTEMPTS, 0, 0
    while attempt < budget:
        attempt += 1
        source = html.read_text(encoding="utf-8")
        nodes = "\n".join(f"- target {n['target']}: {n['html'][:300]}\n  {n['failureSummary'][:300]}"
                          for n in rule["nodes"][:15])
        prompt = (f"Violation `{rid}` ({rule['impact']}): {rule['help']}\n{rule['helpUrl']}\n"
                  f"Failing nodes:\n{nodes}\n\nFile `{html.name}`:\n```html\n{source}\n```")
        if feedback:
            prompt += f"\n\nFeedback on your previous attempt: {feedback}"
        try:
            # escalate only when the cheap model is stuck: two failed or rejected attempts in a row
            model = ESCALATE_MODEL if stuck >= 2 else MODEL
            raw = llm().chat.completions.with_raw_response.create(
                model=model, temperature=0,
                messages=[{"role": "system", "content": PROMPT["content"]}, {"role": "user", "content": prompt}])
            resp = raw.parse()
            usage["llm_calls"] += 1
            if resp.usage:
                usage["prompt_tokens"] += resp.usage.prompt_tokens
                usage["completion_tokens"] += resp.usage.completion_tokens
            # the LiteLLM proxy reports what the call actually cost; no header (other gateways) = unknown
            cost = float(raw.headers.get("x-litellm-response-cost") or 0)
            usage["cost_usd"] += cost
            m = usage["by_model"].setdefault(model, {"calls": 0, "cost_usd": 0.0})
            m["calls"] += 1
            m["cost_usd"] += cost
            plan = parse_json(resp.choices[0].message.content or "")
            patched, skipped = apply_valid_edits(source, plan.get("edits", []))
            if patched == source:
                raise ValueError("no edit applied. " + "; ".join(skipped[:5]))
            html.write_text(patched, encoding="utf-8", newline="\n")
        except Exception as e:  # bad JSON, no usable edit, API hiccup -> retry with feedback
            stuck += 1
            feedback = f"it failed with {type(e).__name__}: {e}. Try again."
            log(f"  attempt {attempt} failed before audit: {e}")
            neatlogs.log("attempt {attempt} failed before audit", level="warning",
                         attempt=attempt, rule=rid, error=str(e)[:300])
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
            neatlogs.log("attempt {attempt} rejected and rolled back", level="warning", attempt=attempt,
                         rule=rid, nodes_left=left, visual_diff=round(vd, 4), problems=problems)
            html.write_text(source, encoding="utf-8", newline="\n")  # recovery: roll back the bad edit
            stuck += 1
            continue
        neatlogs.log("attempt {attempt} accepted", attempt=attempt, rule=rid, nodes_left=left,
                     visual_diff=round(vd, 4), skipped_edits=len(skipped))
        if left == 0:
            return {"rule": rid, "status": "fixed", "attempts": attempt}
        # partial progress: keep the edit, retry the remaining nodes
        log(f"  attempt {attempt} accepted, {left} nodes left")
        before = after
        shutil.copy(work / "after.png", work / "before.png")
        rule = next(v for v in after["violations"] if v["id"] == rid)
        stuck, budget = 0, min(budget + 1, MAX_ATTEMPTS_PROGRESS)  # progress earns another attempt
        feedback = f"it was accepted, but {left} nodes still fail (listed above). Fix those too."
        if skipped:
            feedback += (" These edits were skipped because their `find` was not an exact, unique copy "
                         "of the current file: " + "; ".join(skipped[:5]))
    left = before["by_rule"].get(rid, 0)
    return {"rule": rid, "status": "partial" if left < start_nodes else "gave-up",
            "attempts": attempt, "last_feedback": feedback}


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
    PROMPT.update(load_prompt())
    state["prompt"] = PROMPT["ref"]
    log(f"system prompt: {PROMPT['ref']}")
    otel_trace.get_current_span().set_attribute("jangkau.prompt", PROMPT["ref"])
    headers = {}
    neatlogs.inject_trace_context(headers)  # traceparent = 00-<trace id>-<span id>-01
    state["trace_id"] = headers.get("traceparent", "-").split("-")[1] if headers else "-"
    log(f"neatlogs trace: {state['trace_id']}")

    with sync_playwright() as pw:
        page = new_page(pw)
        start = time.time()
        if "baseline" not in state:
            base = audit(page, html, out / "baseline.png")
            state["crosscheck"] = {"before": crosscheck(page)}
            state["baseline"] = {"nodes": base["nodes"], "by_rule": base["by_rule"]}
            state["violations"] = [{"id": v["id"], "impact": v["impact"], "help": v["help"],
                                    "tags": v.get("tags", []), "nodes": []} for v in base["violations"]]
        log(f"baseline: {state['baseline']['nodes']} failing nodes across "
            f"{len(state['baseline']['by_rule'])} rules")

        while True:
            current = audit(page, html, out / "before.png")
            todo = sorted((v for v in current["violations"] if v["id"] not in state["done"]),
                          key=lambda v: IMPACT.get(v["impact"], 9))
            if not todo:
                break
            if MAX_COST is not None and usage["cost_usd"] >= MAX_COST:
                # fair use: rules are ordered by impact, so what's left is the least severe
                state["budget_stop"] = {"spent_usd": round(usage["cost_usd"], 4), "max_usd": MAX_COST,
                                        "rules_left": [v["id"] for v in todo]}
                log(f"budget reached (${usage['cost_usd']:.4f} of ${MAX_COST}), leaving {len(todo)} rule(s)")
                neatlogs.log("budget reached", level="warning", **state["budget_stop"])
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
        state.setdefault("crosscheck", {})["after"] = crosscheck(page)
        state["seconds"] = round(time.time() - start, 1)
        state["usage"] = usage
        state_file.write_text(json.dumps(state, indent=2))
    neatlogs.flush()
    try:
        state["delivery"] = {k: v for k, v in neatlogs.get_delivery_diagnostics().items()
                             if isinstance(v, (int, float, str, bool))}
    except Exception as e:  # diagnostics are informational; never fail a run on them
        state["delivery"] = {"error": str(e)}
    write_report(state, out / "report.md")
    return state


def compliance_table(s: dict) -> str:
    """Per rule: WCAG SC, level, EN 301 549 clause and failing elements before -> after."""
    lines = ["| Rule | Impact | WCAG SC | Level | EN 301 549 | Before | After |",
             "|---|---|---|---|---|---|---|"]
    for v in sorted(s.get("violations", []), key=lambda v: IMPACT.get(v["impact"], 9)):
        std = standards(v.get("tags", []))
        lines.append(f"| `{v['id']}` | {v['impact']} | {', '.join(std['wcag']) or '-'} | {std['level'] or '-'} | "
                     f"{', '.join(std['en301549']) or '-'} | {s['baseline']['by_rule'].get(v['id'], 0)} | "
                     f"{s['final']['by_rule'].get(v['id'], 0)} |")
    return "\n".join(lines)


def crosscheck_section(s: dict) -> str:
    c = s.get("crosscheck") or {}
    if "before" not in c:
        return ""
    after = c.get("after", c["before"])
    head = (f"HTML_CodeSniffer errors: **{c['before']['errors']}**" if "after" not in c else
            f"HTML_CodeSniffer errors: **{c['before']['errors']} → {after['errors']}**")
    flat = lambda t: " ".join(t.split()).replace("|", "/").replace("`", "'")  # one table cell
    rows = "\n".join(f"| `{i['code']}` | {flat(i['msg'])} | `{flat(i['html'])[:90]}` |" for i in after["items"][:12])
    return ("\n## Independent cross-check (HTML_CodeSniffer, WCAG2AA)\n\n"
            f"A second engine, the one behind Pa11y, so a fix that only satisfies axe shows up here. {head}\n"
            + (f"\n| Technique | Message | Element |\n|---|---|---|\n{rows}\n" if rows else ""))


def write_report(s: dict, path: Path):
    b, f = s["baseline"]["nodes"], s["final"]["nodes"]
    if s.get("verify") == "audit-only":
        path.write_text(f"""# Jangkau audit ({s['version']})

Target: `{s['target']}`
Failing elements: **{b}** across {len(s['baseline']['by_rule'])} rules

{compliance_table(s)}
{crosscheck_section(s)}""", encoding="utf-8")
        return
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
| Cost (reported by the LiteLLM gateway) | ${s['usage'].get('cost_usd', 0):.4f} ({', '.join(f"{k}: {v['calls']} calls, ${v['cost_usd']:.4f}" for k, v in s['usage'].get('by_model', {}).items()) or '-'}) |
| Budget stop | {f"after ${s['budget_stop']['spent_usd']} of ${s['budget_stop']['max_usd']}, not attempted: {', '.join(s['budget_stop']['rules_left'])}" if s.get('budget_stop') else 'no'} |
| Wall time | {s['seconds']}s |

| Rule | Status | Attempts | Nodes |
|---|---|---|---|
{rows}

## Standards (WCAG 2.x, EN 301 549 for the European Accessibility Act)

{compliance_table(s)}
{crosscheck_section(s)}
System prompt: `{s.get('prompt', 'local')}`  
neatlogs delivery: `{json.dumps(s.get('delivery', {}))}`
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
    ap.add_argument("target", nargs="?", help="HTML file to fix, or an http(s) URL to snapshot first")
    ap.add_argument("--out", type=Path, default=Path("runs") / time.strftime("%Y%m%d-%H%M%S"))
    ap.add_argument("--no-verify", action="store_true", help="baseline mode: accept edits without checks")
    ap.add_argument("--pr", action="store_true", help="write the fix back into the target's git repo and open a PR")
    ap.add_argument("--audit-only", action="store_true", help="audit and report, no fixes and no model key needed")
    ap.add_argument("--sarif", type=Path, help="with --audit-only: write SARIF 2.1.0 for GitHub code scanning")
    ap.add_argument("--fail-on", choices=["never", *IMPACT], default="never",
                    help="exit 1 when a violation of this impact or worse remains (for CI)")
    ap.add_argument("--wait", type=int, default=0, metavar="MS",
                    help="wait this long after load before each audit (pages that animate into place)")
    ap.add_argument("--max-cost", type=float, metavar="USD",
                    help="stop starting new rules once this page has cost this much (fair-use cap)")
    ap.add_argument("--crawl", type=int, metavar="N",
                    help="audit up to N same-origin pages reachable from the URL (audit only, no fixing)")
    ap.add_argument("--sync-prompt", metavar="LABEL", nargs="?", const="production",
                    help="save the local system prompt to the neatlogs prompt registry under LABEL, then exit")
    a = ap.parse_args()
    SETTLE_MS = a.wait
    MAX_COST = a.max_cost
    if a.sync_prompt:
        if not os.getenv("NEATLOGS_API_KEY"):
            sys.exit("--sync-prompt needs NEATLOGS_API_KEY")
        log(sync_prompt(a.sync_prompt))
        sys.exit(0)
    if not a.target:
        ap.error("target is required")
    if a.crawl:
        if not re.match(r"https?://", a.target):
            sys.exit("--crawl needs an http(s) URL")
        with neatlogs.identify(session_id=f"jangkau-{a.out.name}"):
            s = audit_site(a.target, a.crawl, a.out, a.sarif)
        log(f"site audit: {len(s['pages'])} pages, {sum(p['nodes'] for p in s['pages'])} failing elements. "
            f"report: {a.out / 'report.md'}" + (f", sarif: {a.sarif}" if a.sarif else ""))
        neatlogs.flush()
        neatlogs.shutdown()
        if a.fail_on != "never" and any(IMPACT.get(v["impact"], 9) <= IMPACT[a.fail_on] for v in s["violations"]):
            sys.exit(1)
        sys.exit(0)
    if re.match(r"https?://", a.target):
        if a.pr:
            sys.exit("--pr needs a local file in a git repo, not a URL")
        target = snapshot_url(a.target, a.out / "source")
        log(f"snapshot of {a.target} saved to {target}")
    else:
        target = Path(a.target)
        if not target.exists():
            sys.exit(f"not found: {target}")
    with neatlogs.identify(session_id=f"jangkau-{a.out.name}"):
        if a.audit_only:
            s = audit_only(target, a.out, a.sarif)
            log(f"audit: {s['baseline']['nodes']} failing elements. report: {a.out / 'report.md'}"
                + (f", sarif: {a.sarif}" if a.sarif else ""))
            remaining = s["violations"]
        else:
            s = run(target, a.out, verify=not a.no_verify)
            log(f"done: {s['baseline']['nodes']} -> {s['final']['nodes']} failing nodes. report: {a.out / 'report.md'}")
            if a.pr and s["final"]["nodes"] < s["baseline"]["nodes"]:
                open_pr(target, a.out)
            remaining = [v for v in s.get("violations", []) if s["final"]["by_rule"].get(v["id"])]
    neatlogs.flush()
    neatlogs.shutdown()
    if a.fail_on != "never" and any(IMPACT.get(v["impact"], 9) <= IMPACT[a.fail_on] for v in remaining):
        sys.exit(1)
