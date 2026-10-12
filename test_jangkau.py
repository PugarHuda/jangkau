import os

os.environ["NEATLOGS_API_KEY"] = ""  # never export traces from tests (empty, so .env cannot refill it)
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
