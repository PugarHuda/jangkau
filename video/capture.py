"""Capture the real pages shown in the demo video with Playwright (public pages only; the neatlogs
dashboard needs a login and is captured separately). Run from the repo root: python video/capture.py"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "video" / "public" / "shots"
W, H = 1600, 900

PAGES = [  # name, url, full page, wait ms
    ("toko-before", (ROOT / "demo_site" / "toko.html").as_uri(), True, 500),
    ("toko-after", (ROOT / "runs" / "video-toko" / "toko.html").as_uri(), True, 500),
    ("landing", "https://jangkau-jet.vercel.app/", False, 3500),
    ("landing-full", "https://jangkau-jet.vercel.app/", True, 3500),
    ("w3c-before", "https://www.w3.org/WAI/demos/bad/before/home.html", True, 1500),
    ("w3c-after", (ROOT / "runs" / "w3c-bad" / "index.html").as_uri(), True, 1500),
    ("freelancer-before", (ROOT / "runs" / "real-freelancer" / "baseline.png").as_uri(), False, 300),
    ("gh-actions", "https://github.com/PugarHuda/jangkau/actions/workflows/accessibility.yml", False, 2500),
    ("gh-workflow", "https://github.com/PugarHuda/jangkau/blob/main/.github/workflows/accessibility.yml", False, 2500),
    ("gh-pr", "https://github.com/PugarHuda/jangkau/pull/1", False, 2500),
    ("entire", "https://entire.io/gh/PugarHuda/jangkau/commit/9713fcd8e88c8a88519e718dc8e8ac2c7ea883f8", False, 5000),
    ("entire-repo", "https://entire.io/gh/PugarHuda/jangkau", False, 5000),
    ("cfo", "https://cfo.ai/s/eaPiXgVJ6eZosuDO", False, 8000),
    ("cfo-full", "https://cfo.ai/s/eaPiXgVJ6eZosuDO", True, 8000),
]

OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1.5, color_scheme="light")
    for name, url, full, wait in PAGES:
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:  # networkidle can time out on chatty apps; the page is usually there
            print(f"{name}: {type(e).__name__}, capturing anyway")
        page.wait_for_timeout(wait)
        if name.startswith("cfo"):  # the shared page opens a sign-in popover over the model
            page.keyboard.press("Escape")
            for close in page.locator("button:near(:text('Keep your access'), 80)").all()[:1]:
                close.click()
            page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / f"{name}.png"), full_page=full)
        print(name, page.title()[:60])
        page.close()
    # what a screen reader gets from the shop, before and after: the real accessibility tree
    import json
    tree = {}
    for name in ("toko-before", "toko-after"):
        page = ctx.new_page()
        page.goto(dict((n, u) for n, u, *_ in PAGES)[name])
        tree[name] = page.locator("body").aria_snapshot()
        page.close()
    (OUT / "aria.json").write_text(json.dumps(tree, indent=1, ensure_ascii=False), encoding="utf-8")
    browser.close()
