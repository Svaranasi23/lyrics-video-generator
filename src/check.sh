#!/bin/sh
# Rebuild the page from the spreadsheet export and run the regression tests.
set -e
cd "$(dirname "$0")"
python3 -I build.py data/gg.xlsx template.html dist/index.html
python3 -I tests/test_page.py dist/index.html
