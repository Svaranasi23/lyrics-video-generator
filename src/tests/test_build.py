"""Unit tests for build.py (no browser needed). Run: python tests/test_build.py"""
import os
import sys
import tempfile

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import build  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


def make(songs, verses, lines, videos):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name, header, data in (
        ("Songs", ["song_no", "title", "raga"], songs),
        ("Verses", ["song_no", "verse", "kind", "meaning_te", "meaning_en"], verses),
        ("Lines", ["song_no", "verse", "line_no", "devanagari", "telugu", "transliteration", "telugu_phonetic"], lines),
        ("Videos", ["song_no", "label", "youtube_url", "start_sec", "end_sec"], videos),
    ):
        ws = wb.create_sheet(name)
        ws.append(header)
        for r in data:
            ws.append(r)
    f = os.path.join(tempfile.mkdtemp(), "t.xlsx")
    wb.save(f)
    return f


def raises(f, text):
    try:
        build.build_data(f)
    except ValueError as e:
        return text in str(e)
    return False


S = [[1, "Alpha", "Todi"], [2, "Beta", None]]
V = [[1, "S1.1", "sloka", None, None], [1, "G1", "gitam", "అర్థం", "meaning one"], [1, "G2", "gitam", None, None]]
L = [[1, "G1", 2, "d2", "t2", "e2", "p2"], [1, "G1", 1, "d1", "t1", "e1", "p1"],
     [1, "S1.1", 1, "ds", "ts", "es", "ps"], [1, "G2", 1, "d3", "t3", "e3", "p3"], [1, "G2", 2, "", "", "", ""]]
VID = [[1, "Final pick", "https://www.youtube.com/watch?v=abc123", None, None],
       [1, "Chapter", "https://www.youtube.com/watch?v=zzz999&t=30", None, 120],
       [1, "Blank link", None, None, None],
       [2, "Short", "https://youtu.be/xyz?t=5", 7, None]]

d = build.build_data(make(S, V, L, VID))
s1, s2 = d["songs"]
check("two songs, sorted", [s["no"] for s in d["songs"]] == [1, 2])
check("lines ordered by line_no", [l["te"] for l in s1["lines"][:2]] == ["t1", "t2"])
check("sloka goes to slokas, not lines", [l["te"] for l in s1["slokas"]] == ["ts"] and len(s1["lines"]) == 3)
check("blank Telugu row ignored", len(s1["lines"]) == 3)
check("verse labels", s1["lines"][0]["v"] == 1 and s1["slokas"][0]["v"] == "Sarga 1.1")
check("meaning on first line of verse only", "mean" in s1["lines"][0] and "mean" not in s1["lines"][1])
check("meaning text kept", s1["lines"][0]["mean"] == {"te": "అర్థం", "en": "meaning one"})
check("blank meaning publishes nothing", "mean" not in s1["lines"][2] and "mean" not in s1["slokas"][0])
check("song with no lines is kept", s2["lines"] == [] and s2["title"] == "Beta" and s2["raga"] == "")
check("multiple videos per song", [x["label"] for x in s1["sources"]] == ["Final pick", "Chapter"])
check("blank video link skipped", len(s1["sources"]) == 2)
check("start/end from columns, start from URL otherwise",
      s1["sources"][1]["start"] == 30 and s1["sources"][1]["end"] == 120 and s2["sources"][0]["start"] == 7)
check("dash cell counts as blank", build.cell("-") == "" and build.cell(None) == "" and build.cell(" x ") == "x")

check("error: line points at unknown verse", raises(make(S, V, [[1, "G9", 1, "", "t", "", ""]], VID), "G9"))
check("error: duplicate verse", raises(make(S, V + [[1, "G1", "gitam", None, None]], L, VID), "duplicate"))
check("error: video for unknown song", raises(make(S, V, L, [[9, "x", "https://youtu.be/a", None, None]]), "song 9"))
wb = openpyxl.load_workbook(make(S, V, L, VID))
del wb["Videos"]
nov = os.path.join(tempfile.mkdtemp(), "nov.xlsx")
wb.save(nov)
check("error: missing tab", raises(nov, "missing tab: Videos"))

real = os.path.join(os.path.dirname(__file__), "..", "data", "gg-template.xlsx")
if os.path.exists(real):
    r = build.build_data(real)
    check("real file: 24 songs", len(r["songs"]) == 24, len(r["songs"]))
    check("real file: lyrics missing only for 16, 21, 22",
          [s["no"] for s in r["songs"] if not s["lines"]] == [16, 21, 22])

sys.exit(1 if FAILS else 0)
