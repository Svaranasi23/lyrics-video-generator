"""Check that the browser reader (live/live_data.js) builds exactly what build.py builds.

Usage: ../.venv/bin/python tests/parity_live.py data/gg-template.xlsx
Exports each tab to CSV (like Google's "publish to web"), runs live_data.js in Node, compares to build.py.
"""
import csv
import io
import json
import os
import subprocess
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import build  # noqa: E402

path = sys.argv[1]
wb = openpyxl.load_workbook(path, data_only=True)


def tab_csv(name):
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    for row in wb[name].iter_rows(values_only=True):
        w.writerow(["" if v is None else v for v in row])
    return out.getvalue()


tabs = {k: tab_csv(v) for k, v in {"songs": "Songs", "verses": "Verses", "lines": "Lines", "videos": "Videos"}.items()}
js = ("const {buildData}=require(process.argv[1]);"
      "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>"
      "process.stdout.write(JSON.stringify(buildData(JSON.parse(s),'T'))));")
res = subprocess.run(["node", "-e", js, os.path.join(HERE, "..", "live", "live_data.js")],
                     input=json.dumps(tabs), capture_output=True, text=True, check=True)
live = json.loads(res.stdout)
ref = build.build_data(path, "T")
if live == ref:
    print(f"PASS live reader matches build.py ({len(ref['songs'])} songs, "
          f"{sum(len(s['lines']) for s in ref['songs'])} lines, "
          f"{sum(len(s['sources']) for s in ref['songs'])} videos)")
else:
    for a, b in zip(live["songs"], ref["songs"]):
        if a != b:
            print("FAIL first difference in song", a["no"], {k: (a[k] == b[k]) for k in a})
            break
    sys.exit(1)
