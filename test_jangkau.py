import os

os.environ["NEATLOGS_API_KEY"] = ""  # never export traces from tests (empty, so .env cannot refill it)
os.environ["NEATLOGS_TRACE_URL"] = ""  # bare trace IDs, whatever the local .env links to
os.environ.setdefault("LITELLM_API_KEY", "test")

import pytest  # noqa: E402

from jangkau import apply_edits, parse_json, visual_diff  # noqa: E402


def test_apply_edits_replaces_unique_match():
    assert apply_edits("<img src=a>", [{"find": "<img src=a>", "replace": '<img src=a alt="x">'}]) == '<img src=a alt="x">'


def test_apply_edits_rejects_ambiguous_or_missing_find():
    with pytest.raises(ValueError, match="matched 2 times"):
        apply_edits("<p></p><p></p>", [{"find": "<p>", "replace": "<p lang=id>"}])
    with pytest.raises(ValueError, match="matched 0 times"):
        apply_edits("<p></p>", [{"find": "<div>", "replace": ""}])


def test_parse_json_tolerates_prose_around_json():
    assert parse_json('sure!\n```json\n{"edits": []}\n```') == {"edits": []}
    with pytest.raises(ValueError):
        parse_json("no json here")


def test_visual_diff_layout_ignores_recolour_but_not_moves(tmp_path):
    from PIL import Image, ImageDraw
    def shot(name, fill, dx=0):
        im = Image.new("RGB", (200, 100), "white")
        ImageDraw.Draw(im).rectangle((20 + dx, 20, 180 + dx, 80), fill=fill, outline="black")
        im.save(tmp_path / name)
        return tmp_path / name
    a, recoloured, moved = shot("a.png", "#1abc9c"), shot("b.png", "#117964"), shot("c.png", "#1abc9c", dx=15)
    assert visual_diff(a, recoloured) > 0.35            # raw pixels: recolour looks huge
    assert visual_diff(a, recoloured, layout=True) < 0.05
    assert visual_diff(a, moved, layout=True) > 0.005   # edges moved


def test_standards_maps_axe_tags_to_wcag_and_en301549():
    from jangkau import standards
    tags = ["cat.color", "wcag2aa", "wcag143", "wcag1410", "EN-301-549", "EN-9.1.4.3", "ACT"]
    assert standards(tags) == {"wcag": ["1.4.10", "1.4.3"], "level": "AA", "en301549": ["9.1.4.3"]}
    assert standards(["best-practice"])["level"] == "best practice"


def test_slim_span_keeps_decision_data_and_drops_bulk():
    import json
    from jangkau import slim_span
    node = {"html": "<img src=x>" + "y" * 400, "target": ["img"], "failureSummary": "Fix any",
            "any": [{"id": "has-alt", "relatedNodes": [], "message": "x" * 500}], "all": [], "none": []}
    audit = {"violations": [{"id": "image-alt", "impact": "critical", "help": "Images need alt",
                             "tags": ["wcag111"] * 50, "description": "d" * 300, "nodes": [node] * 5}],
             "nodes": 5, "by_rule": {"image-alt": 5}}
    raw = json.dumps(audit)
    span = slim_span({"attributes": {"output": raw, "small": "keep"}})
    slim = json.loads(span["attributes"]["output"])
    assert len(span["attributes"]["output"]) < len(raw) / 3 and span["attributes"]["small"] == "keep"
    v = slim["violations"][0]
    assert v["id"] == "image-alt" and v["impact"] == "critical" and "tags" not in v
    assert len(v["nodes"][0]["html"]) == 200 and v["nodes"][0]["target"] == ["img"] and "any" not in v["nodes"][0]
    assert slim["by_rule"] == {"image-alt": 5}


def test_find_line_handles_reserialised_and_repeated_elements():
    from jangkau import find_line
    src = '<p>\n<input type="email" id="e">\n<a href="#">x</a>\n<abbr>y</abbr>\n<a href="#">z</a>\n'
    assert find_line(src, '<input type="email" id="e" style="">') == 2  # browser added style=""
    assert find_line(src, '<a href="#">z</a>', nth=1) == 5
    assert find_line(src, '<a class="new">') == 3  # bare tag fallback never matches <abbr>
    assert find_line(src, "<html>") == 1


def test_apply_valid_edits_keeps_good_edits_and_reports_bad_ones():
    from jangkau import apply_valid_edits
    src = "<img a><img b><p>x</p><p>x</p>"
    out, errors = apply_valid_edits(src, [{"find": "<img a>", "replace": "<img a alt=1>"},
                                          {"find": "<img zzz>", "replace": "nope"},
                                          {"find": "<p>x</p>", "replace": "ambiguous"},
                                          {"find": "<img b>", "replace": "<img b alt=2>"}])
    assert out == "<img a alt=1><img b alt=2><p>x</p><p>x</p>"
    assert len(errors) == 2 and "matched 0 times" in errors[0] and "matched 2 times" in errors[1]


def test_prompt_falls_back_to_local_without_a_key():
    import jangkau
    assert jangkau.load_prompt() == {"content": jangkau.SYSTEM, "ref": "local"}


def test_report_shows_gateway_cost_and_budget_stop(tmp_path):
    from jangkau import write_report
    s = {"target": "p.html", "version": "t", "verify": True, "trace_id": "x", "results": [],
         "baseline": {"nodes": 10, "by_rule": {"label": 4, "region": 6}}, "final": {"nodes": 6, "by_rule": {"region": 6}},
         "violations": [], "seconds": 1.0,
         "usage": {"llm_calls": 2, "prompt_tokens": 10, "completion_tokens": 5, "cost_usd": 0.0245,
                   "by_model": {"claude-sonnet-4.6": {"calls": 2, "cost_usd": 0.0245}}},
         "budget_stop": {"spent_usd": 0.0245, "max_usd": 0.02, "rules_left": ["region"]}}
    write_report(s, tmp_path / "r.md")
    r = (tmp_path / "r.md").read_text(encoding="utf-8")
    assert "| Cost (reported by the LiteLLM gateway) | $0.0245 (claude-sonnet-4.6: 2 calls, $0.0245) |" in r
    assert "| Budget stop | after $0.0245 of $0.02, not attempted: region |" in r


def test_provenance_stamp_and_trailers():
    from jangkau import commit_trailers, provenance, stamp_html
    s = {"trace_id": "abc123", "prompt": "jangkau-fixer-system@v1 (production)", "version": "v8",
         "baseline": {"nodes": 47}, "final": {"nodes": 0}}
    p = provenance(s)
    page = "<!DOCTYPE html>\n<html><body>x</body></html>"
    once = stamp_html(page, p)
    assert once.startswith("<!DOCTYPE html>\n<!-- Jangkau: accessibility fixes, 47 -> 0 failing elements")
    assert "neatlogs trace abc123, prompt jangkau-fixer-system@v1 (production), v8. -->" in once
    assert stamp_html(once, p) == once  # a re-run replaces the stamp instead of adding another
    assert commit_trailers(p) == ("Jangkau-Trace: abc123\nJangkau-Prompt: jangkau-fixer-system@v1 (production)\n"
                                  "Jangkau-Result: 47 -> 0 failing elements")
