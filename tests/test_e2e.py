"""End-to-end checks with a real browser: the landing page, the audit-only CLI and its SARIF.
No model calls; the fixing loop is covered by the traced runs in runs/."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SITE = (ROOT / "site" / "index.html").as_uri()
ENV = {**os.environ, "NEATLOGS_API_KEY": "", "LITELLM_API_KEY": ""}  # prove no secrets are needed


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        yield b
        b.close()


def open_site(browser, **ctx):
    page = browser.new_context(**ctx).new_page()
    page.goto(SITE)
    page.wait_for_timeout(3200)  # let the hero contrast animation finish
    return page


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_landing_page_has_no_axe_violations(browser, scheme):
    page = open_site(browser, color_scheme=scheme)
    violations = Axe().run(page).response["violations"]
    assert violations == [], [(v["id"], [n["html"][:80] for n in v["nodes"]]) for v in violations]


def test_hero_ends_on_passing_contrast(browser):
    page = open_site(browser)
    ratio = float(page.text_content("#ratio").split(":")[0])
    assert ratio >= 4.5 and page.text_content("#verdict") == "passes WCAG"


def test_reduced_motion_skips_animation(browser):
    page = browser.new_context(reduced_motion="reduce").new_page()
    page.goto(SITE)
    page.wait_for_timeout(300)
    assert page.text_content("#verdict") == "passes WCAG"


@pytest.mark.parametrize("width", [320, 375, 768, 1440])
def test_no_horizontal_scroll(browser, width):
    page = open_site(browser, viewport={"width": width, "height": 800})
    assert page.evaluate("document.documentElement.scrollWidth") <= width


def test_before_after_toggle(browser):
    page = open_site(browser)
    before, after = page.locator(".toggle button").all()
    after.click()
    assert after.get_attribute("aria-pressed") == "true" and before.get_attribute("aria-pressed") == "false"
    frame = page.locator("#shop")
    assert frame.get_attribute("src") == "after/shop.html" and "fixed by Jangkau" in frame.get_attribute("title")
    page.wait_for_timeout(800)
    fixed = page.frame_locator("#shop").locator("html")
    assert fixed.get_attribute("lang") == "en"  # the fixed page really loaded
    before.click()
    assert frame.get_attribute("src") == "before/shop.html"


def test_toggle_counts_match_the_real_pages(browser):
    """The 47 / 0 on the buttons must be what axe finds on the shipped before/after pages."""
    page = open_site(browser)
    counts = [int(c) for c in page.locator(".toggle .count").all_text_contents()]
    found = []
    for name in ("before", "after"):
        p = browser.new_page()
        p.goto((ROOT / "site" / name / "shop.html").as_uri())
        found.append(sum(len(v["nodes"]) for v in Axe().run(p).response["violations"]))
    assert counts == found


def test_keyboard_focus_is_visible(browser):
    page = open_site(browser)
    for _ in range(6):
        page.keyboard.press("Tab")
        style = page.evaluate("""() => { const s = getComputedStyle(document.activeElement);
                                        return [document.activeElement.tagName, s.outlineStyle, s.outlineWidth]; }""")
        assert style[0] != "BODY" and style[1] != "none" and style[2] != "0px", style


def test_in_page_links_resolve(browser):
    page = open_site(browser)
    anchors = page.eval_on_selector_all("a[href^='#']", "els => els.map(e => e.getAttribute('href'))")
    missing = [a for a in anchors if a != "#" and not page.query_selector(a)]
    assert not missing


def test_assets_exist():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    for ref in re.findall(r'(?:src|data-src)="([^":#]+)"', html):
        assert (ROOT / "site" / ref).exists(), ref
    assert (ROOT / "site" / "og.png").exists()


def run_cli(*args):
    return subprocess.run([sys.executable, str(ROOT / "jangkau.py"), *args], cwd=ROOT, env=ENV,
                          capture_output=True, text=True, timeout=300)


def test_audit_only_cli_writes_sarif_and_fails_ci(tmp_path):
    out, sarif = tmp_path / "audit", tmp_path / "a.sarif"
    r = run_cli("demo_site/shop.html", "--audit-only", "--out", str(out), "--sarif", str(sarif), "--fail-on", "serious")
    assert r.returncode == 1, r.stderr[-500:]
    doc = json.loads(sarif.read_text(encoding="utf-8"))
    run = doc["runs"][0]
    assert doc["version"] == "2.1.0" and len(run["results"]) == 47
    contrast = next(x for x in run["tool"]["driver"]["rules"] if x["id"] == "color-contrast")
    assert contrast["properties"]["wcag"] == ["1.4.3"] and contrast["properties"]["en301549"] == ["9.1.4.3"]
    src = (ROOT / "demo_site" / "shop.html").read_text(encoding="utf-8").splitlines()
    for res in run["results"]:  # every element-level result points at a line holding that element
        line = res["locations"][0]["physicalLocation"]["region"]["startLine"]
        tag = re.search(r": (<\w+)", res["message"]["text"]).group(1)
        assert tag == "<html" or tag in src[line - 1], (res["ruleId"], line, tag)
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 18 |" in report


def test_audit_only_passes_on_the_fixed_page(tmp_path):
    r = run_cli("site/after/shop.html", "--audit-only", "--out", str(tmp_path), "--fail-on", "minor")
    assert r.returncode == 0, r.stdout[-500:] + r.stderr[-500:]


def test_sarif_matches_official_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = Path(os.environ.get("SARIF_SCHEMA", Path.home() / "AppData/Local/Temp/sarif-schema.json"))
    if not schema.exists():
        pytest.skip("download https://json.schemastore.org/sarif-2.1.0.json and set SARIF_SCHEMA")
    sarif = tmp_path / "a.sarif"
    run_cli("demo_site/index.html", "--audit-only", "--out", str(tmp_path / "o"), "--sarif", str(sarif))
    jsonschema.validate(json.loads(sarif.read_text(encoding="utf-8")), json.loads(schema.read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    """A real HTTP server with a small site: two pages in /docs/, one outside it, one image link."""
    import functools
    import http.server
    import threading
    root = tmp_path_factory.mktemp("site")
    (root / "docs").mkdir()
    (root / "docs" / "index.html").write_text(
        '<html><body><a href="b.html">b</a> <a href="../outside.html">out</a> <a href="pic.png">pic</a>'
        '<a href="b.html#top">b again</a></body></html>')
    (root / "docs" / "b.html").write_text(
        '<html lang="en"><head><title>b</title></head><body><main><h1>b</h1>'
        '<a href="index.html" onfocus="this.blur()">home</a></main></body></html>')
    (root / "outside.html").write_text("<html><body>outside</body></html>")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_crawl_stays_in_scope_and_merges_sarif(site, tmp_path):
    sarif = tmp_path / "site.sarif"
    r = run_cli(f"{site}/docs/index.html", "--crawl", "10", "--out", str(tmp_path / "o"), "--sarif", str(sarif),
                "--fail-on", "serious")
    assert r.returncode == 1, r.stdout[-800:] + r.stderr[-800:]  # b.html drops focus: serious
    report = (tmp_path / "o" / "report.md").read_text(encoding="utf-8")
    assert "Pages audited: **2**" in report and "outside" not in report
    uris = {res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            for res in json.loads(sarif.read_text(encoding="utf-8"))["runs"][0]["results"]}
    assert uris == {f"{site}/docs/index.html", f"{site}/docs/b.html"}


def test_custom_rule_catches_focus_removal(tmp_path):
    page = tmp_path / "p.html"
    page.write_text('<html lang="en"><head><title>t</title></head><body><main><h1>t</h1>'
                    '<a href="#" onfocus="blur();">a</a><button onfocus="track()">b</button></main></body></html>')
    run_cli(str(page), "--audit-only", "--out", str(tmp_path / "o"))
    report = (tmp_path / "o" / "report.md").read_text(encoding="utf-8")
    assert "| `focus-not-removed` | serious | 2.1.1, 2.4.7 | A | 9.2.1.1, 9.2.4.7 | 1 |" in report  # not the button


def test_crosscheck_reports_second_engine(tmp_path):
    run_cli("demo_site/shop.html", "--audit-only", "--out", str(tmp_path))
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "## Independent cross-check (HTML_CodeSniffer, WCAG2AA)" in report
    n = int(re.search(r"HTML_CodeSniffer errors: \*\*(\d+)\*\*", report).group(1))
    assert n > 10  # the broken shop fails the second engine too


def test_cli_requires_a_target_and_url_for_crawl():
    assert "target is required" in run_cli().stderr
    assert "--crawl needs an http(s) URL" in run_cli("demo_site/shop.html", "--crawl", "2").stderr


def test_vercel_protection_bypass_header_reaches_the_server(tmp_path):
    """A server that, like a protected Vercel preview, only serves the page to the bypass header."""
    import http.server
    import threading

    class Protected(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            ok = self.headers.get("x-vercel-protection-bypass") == "s3cret"
            body = (b'<html lang="en"><head><title>app</title></head><body><main><h1>app</h1></main></body></html>'
                    if ok else b"<html><body><img src=x.png> Log in to Vercel</body></html>")
            self.send_response(200)
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Protected)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"
    try:
        locked = run_cli(url, "--audit-only", "--out", str(tmp_path / "a"))
        env = {**ENV, "VERCEL_AUTOMATION_BYPASS_SECRET": "s3cret"}
        opened = subprocess.run([sys.executable, str(ROOT / "jangkau.py"), url, "--audit-only", "--out", str(tmp_path / "b")],
                                cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    finally:
        server.shutdown()
    assert "Log in to Vercel" in (tmp_path / "a" / "source" / "index.html").read_text(encoding="utf-8")
    assert "<h1>app</h1>" in (tmp_path / "b" / "source" / "index.html").read_text(encoding="utf-8")
    assert "audit: 0 failing elements" in opened.stdout, opened.stdout[-400:] + locked.stdout[-200:]
