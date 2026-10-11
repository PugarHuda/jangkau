import os

os.environ.pop("NEATLOGS_API_KEY", None)  # never export traces from tests
os.environ.setdefault("OPENAI_API_KEY", "test")

import pytest  # noqa: E402

from jangkau import apply_edits, parse_json  # noqa: E402


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
