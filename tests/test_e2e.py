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
    assert frame.get_attribute("src") == "after/toko.html" and "fixed by Jangkau" in frame.get_attribute("title")
    page.wait_for_timeout(800)
    fixed = page.frame_locator("#shop").locator("html")
    assert fixed.get_attribute("lang") == "id"  # the fixed page really loaded
    before.click()
    assert frame.get_attribute("src") == "before/toko.html"


def test_toggle_counts_match_the_real_pages(browser):
    """The 47 / 0 on the buttons must be what axe finds on the shipped before/after pages."""
    page = open_site(browser)
    counts = [int(c) for c in page.locator(".toggle .count").all_text_contents()]
    found = []
    for name in ("before", "after"):
        p = browser.new_page()
        p.goto((ROOT / "site" / name / "toko.html").as_uri())
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
    r = run_cli("demo_site/toko.html", "--audit-only", "--out", str(out), "--sarif", str(sarif), "--fail-on", "serious")
    assert r.returncode == 1, r.stderr[-500:]
    doc = json.loads(sarif.read_text(encoding="utf-8"))
    run = doc["runs"][0]
    assert doc["version"] == "2.1.0" and len(run["results"]) == 47
    contrast = next(x for x in run["tool"]["driver"]["rules"] if x["id"] == "color-contrast")
    assert contrast["properties"]["wcag"] == ["1.4.3"] and contrast["properties"]["en301549"] == ["9.1.4.3"]
    src = (ROOT / "demo_site" / "toko.html").read_text(encoding="utf-8").splitlines()
    for res in run["results"]:  # every element-level result points at a line holding that element
        line = res["locations"][0]["physicalLocation"]["region"]["startLine"]
        tag = re.search(r": (<\w+)", res["message"]["text"]).group(1)
        assert tag == "<html" or tag in src[line - 1], (res["ruleId"], line, tag)
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "| `color-contrast` | serious | 1.4.3 | AA | 9.1.4.3 | 18 |" in report


def test_audit_only_passes_on_the_fixed_page(tmp_path):
    r = run_cli("site/after/toko.html", "--audit-only", "--out", str(tmp_path), "--fail-on", "minor")
    assert r.returncode == 0, r.stdout[-500:] + r.stderr[-500:]


def test_sarif_matches_official_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = Path(os.environ.get("SARIF_SCHEMA", Path.home() / "AppData/Local/Temp/sarif-schema.json"))
    if not schema.exists():
        pytest.skip("download https://json.schemastore.org/sarif-2.1.0.json and set SARIF_SCHEMA")
    sarif = tmp_path / "a.sarif"
    run_cli("demo_site/index.html", "--audit-only", "--out", str(tmp_path / "o"), "--sarif", str(sarif))
    jsonschema.validate(json.loads(sarif.read_text(encoding="utf-8")), json.loads(schema.read_text(encoding="utf-8")))
