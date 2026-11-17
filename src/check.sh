#!/bin/sh
# Rebuild the page from the template workbook and run the tests.
# Uses the project's .venv (has openpyxl). Page test needs Playwright + Chrome (the user's Mac only).
set -e
cd "$(dirname "$0")"
PY=../.venv/bin/python
[ -x "$PY" ] || PY=python3
$PY tests/test_build.py
$PY build.py data/gg-template.xlsx template.html dist/index.html
if $PY -c "import playwright" 2>/dev/null; then
  $PY tests/test_page.py dist/index.html
else
  echo "skipping tests/test_page.py (Playwright not installed)"
fi
