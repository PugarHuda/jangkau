#!/usr/bin/env bash
# Publish site/ to GitHub Pages (gh-pages branch).
set -euo pipefail
cd "$(dirname "$0")/.."
git push -f origin "$(git subtree split --prefix site)":refs/heads/gh-pages
