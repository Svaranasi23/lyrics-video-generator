#!/bin/sh
# Run the tests. The page reads the published Google Sheet live, so there is no build step any more.
# Python tests use the project's .venv (has openpyxl); the reader tests run in Node.
set -e
cd "$(dirname "$0")"
PY=../.venv/bin/python
[ -x "$PY" ] || PY=python3
node tests/test_live_data.js
$PY tests/test_build.py
[ -f data/gg-template.xlsx ] && $PY tests/parity_live.py data/gg-template.xlsx
echo "(tests/test_page.py is out of date: it expects the old baked-in page)"
