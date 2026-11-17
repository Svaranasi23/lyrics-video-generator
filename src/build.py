"""Build the Gita Govindam sing-along page from the spreadsheet export.

Usage: python3 -I build.py data/gg.xlsx template.html dist/index.html
"""
import json
import re
import sys
from urllib.parse import parse_qs, urlparse

import openpyxl

XLSX, TEMPLATE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def yt_id(url):
    """Return (video_id, start_seconds) for a YouTube URL, else None."""
    if not url:
        return None
    u = urlparse(url)
    host = u.netloc.lower()
    vid = None
    if "youtu.be" in host:
        vid = u.path.lstrip("/").split("/")[0]
    elif "youtube.com" in host and "music." not in host:
        vid = parse_qs(u.query).get("v", [None])[0]
    if not vid:
        return None
    t = parse_qs(u.query).get("t", ["0"])[0]
    start = int(re.sub(r"\D", "", t) or 0)
    return vid, start


def clean_segment(s):
    s = s.replace("!", " ")
    s = re.sub(r"[0-9०-९]+\s*$", "", s.strip())  # trailing verse number
    s = re.sub(r"\s+", " ", s).strip(" -")
    return s.strip()


REFRAIN_SPLIT = {  # song 1 rows have no '~'; split before the Keshava refrain
    "te": "కేశవ", "dev": "केशव", "en": "keshava", "tes": "కేశవ",
}


def split_lines(cols, song_no):
    parts = {k: str(v or "").split("~") for k, v in cols.items()}
    n = len(parts["te"])
    if any(len(p) != n for p in parts.values()):
        raise ValueError(f"line count mismatch in song {song_no}")
    if n == 1 and song_no == 1:
        for k, p in parts.items():
            s = p[0]
            idx = s.find(REFRAIN_SPLIT[k])
            parts[k] = [s[:idx], s[idx:]] if idx > 0 else [s]
        n = len(parts["te"])
    lines = []
    for i in range(n):
        line = {k: clean_segment(parts[k][i]) for k in parts}
        if line["te"]:
            lines.append(line)
    return lines


wb = openpyxl.load_workbook(XLSX)
raw = wb["Geethagovindam_raw"]
index = wb["Index"]

# --- lyrics: Gitam rows grouped by song; preceding Sarga slokas kept as optional intro
songs_lyrics, pending_slokas = {}, []
for r in raw.iter_rows(min_row=2):
    label = str(r[1].value or "").strip()
    cols = {"dev": r[3].value, "te": r[4].value, "en": r[5].value, "tes": r[6].value}
    m = re.match(r"Gitam (\d+)\.(\d+)", label)
    if m:
        song, verse = int(m.group(1)), int(m.group(2))
        if song not in songs_lyrics:
            songs_lyrics[song] = {"slokas": pending_slokas, "lines": []}
            pending_slokas = []
        entry = songs_lyrics[song]
        for ln in split_lines(cols, song):
            ln["v"] = verse
            entry["lines"].append(ln)
    elif label.startswith("Sarga"):
        for ln in split_lines(cols, 0):
            ln["v"] = label
            pending_slokas.append(ln)
    elif label.startswith(("Dhyanam", "Appendix")):  # invocations, not a song intro
        pending_slokas = []

COMPILATION = "MTCehEEK8tA"

# --- index: titles, raga, video sources
songs = []
chapter_starts = {}
for r in index.iter_rows(min_row=2, max_row=40):
    if r[0].value is None:
        continue
    no = int(float(r[0].value))
    i_cell = r[8]
    yt = yt_id(i_cell.hyperlink.target) if i_cell.hyperlink else None
    if yt:
        chapter_starts[no] = yt[1]

ordered = sorted(chapter_starts)
for r in index.iter_rows(min_row=2, max_row=40):
    if r[0].value is None:
        continue
    no = int(float(r[0].value))
    sources = []
    seen = set()

    def add(label, vid, start=0, end=None):
        key = (vid, start)
        if key in seen:
            return
        seen.add(key)
        sources.append({"label": label, "id": vid, "start": start, "end": end})

    # chapter in the Saindhavi compilation
    comp = None
    if no in chapter_starts:
        nxt = [s for s in ordered if s > no]
        end = chapter_starts[nxt[0]] if nxt else None
        comp = (chapter_starts[no], end)

    d = r[3]
    if d.hyperlink:
        y = yt_id(d.hyperlink.target)
        if y and y[0] == COMPILATION and comp:
            add("Saindhavi (Final pick)", COMPILATION, comp[0], comp[1])
        elif y:
            add("Final pick", y[0], y[1])
    if comp:
        add("Saindhavi (compilation)", COMPILATION, comp[0], comp[1])
    for c in (r[4], r[5], r[6]):
        if c.hyperlink:
            y = yt_id(c.hyperlink.target)
            if y and y[0] != COMPILATION:
                add(re.sub(r"\s*\(YouTube[^)]*\)", "", str(c.value)), y[0], y[1])

    lyr = songs_lyrics.get(no, {"slokas": [], "lines": []})
    songs.append({
        "no": no,
        "title": str(r[1].value).strip(),
        "raga": str(r[2].value or "").strip(),
        "sources": sources,
        "slokas": lyr["slokas"],
        "lines": lyr["lines"],
    })

data = {"collection": "Gita Govindam — Ashtapadi", "songs": songs}
html = open(TEMPLATE, encoding="utf-8").read()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
html = html.replace("/*__DATA__*/null", payload)
import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)

missing = [s["no"] for s in songs if not s["lines"]]
print(f"songs={len(songs)} lines={sum(len(s['lines']) for s in songs)} "
      f"missing_lyrics={missing} no_video={[s['no'] for s in songs if not s['sources']]}")
for s in songs[:4] + songs[-1:]:
    print(s["no"], s["title"], [(x["label"], x["id"], x["start"], x["end"]) for x in s["sources"]],
          "slokas", len(s["slokas"]), "lines", len(s["lines"]))
