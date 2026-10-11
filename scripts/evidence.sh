#!/usr/bin/env bash
# Re-runs the before/after comparison with neatlogs export on, one trace per version.
#   v1: current code, --no-verify (no checks)
#   v2: the first verifier (commit 963a4dd), strict and naive
#   v4: current code, the verifier fixed using v2's run data
# Filter traces in neatlogs by tag version:v1 / version:v2 / version:v4.
set -euo pipefail
cd "$(dirname "$0")/.."
grep -q '^NEATLOGS_API_KEY=.\+' .env || { echo "set NEATLOGS_API_KEY in .env first"; exit 1; }

PY=.venv/Scripts/python; [ -x "$PY" ] || PY=.venv/bin/python
PAGE=${PAGE:-demo_site/toko.html}
export JANGKAU_MODEL=${JANGKAU_MODEL:-claude-haiku}
STAMP=$(date +%H%M%S)

[ -d .v2 ] || git worktree add -q .v2 963a4dd

JANGKAU_VERSION=v1 "$PY" jangkau.py "$PAGE" --no-verify --out "runs/ev-$STAMP-v1"
JANGKAU_VERSION=v2 "$PY" .v2/jangkau.py "$PAGE" --out "runs/ev-$STAMP-v2"
JANGKAU_VERSION=v4 "$PY" jangkau.py "$PAGE" --out "runs/ev-$STAMP-v4"

for v in v1 v2 v4; do echo "== $v"; sed -n '5,12p' "runs/ev-$STAMP-$v/report.md"; done
