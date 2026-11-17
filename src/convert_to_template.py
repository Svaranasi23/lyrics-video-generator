"""Convert the old Ashtapadi export into the standard template tabs (Songs, Verses, Lines).

Usage: .venv/bin/python src/convert_to_template.py src/data/gg.xlsx [song numbers...]
Preview only for now: prints tables, writes nothing.
"""
import re
import sys

import openpyxl

SCRIPTS = {"dev": 3, "te": 4, "en": 5, "tes": 6}  # column indexes in Geethagovindam_raw
REFRAIN = {"te": "కేశవ", "dev": "केशव", "en": "keshava", "tes": "కేశవ"}  # song 1 has no '~'


def clean(s):
    s = s.replace("!", " ")
    s = re.sub(r"[0-9०-९]+\s*$", "", s.strip())  # trailing verse number
    return re.sub(r"\s+", " ", s).strip(" -").strip()


def split_lines(cols, song):
    parts = {k: str(v or "").split("~") for k, v in cols.items()}
    n = len(parts["te"])
    if any(len(p) != n for p in parts.values()):
        raise ValueError(f"line count mismatch in song {song}")
    if n == 1 and song == 1:
        for k, p in parts.items():
            i = p[0].find(REFRAIN[k])
            parts[k] = [p[0][:i], p[0][i:]] if i > 0 else [p[0]]
        n = len(parts["te"])
    out = []
    for i in range(n):
        line = {k: clean(parts[k][i]) for k in parts}
        if line["te"]:
            out.append(line)
    return out


def convert(path):
    wb = openpyxl.load_workbook(path)
    verses, lines, pending = [], [], []  # pending = intro slokas waiting for their song
    for r in wb["Geethagovindam_raw"].iter_rows(min_row=2):
        label = str(r[1].value or "").strip()
        cols = {k: r[i].value for k, i in SCRIPTS.items()}
        meaning = str(r[7].value or "").strip()
        meaning = "" if meaning in ("-", "") else meaning
        m = re.match(r"Gitam (\d+)\.(\d+)", label)
        if m:
            song, v = int(m.group(1)), int(m.group(2))
            for p in pending:  # attach intro slokas to this song
                p["verse"]["song"] = song
                verses.append(p["verse"])
                lines.extend(dict(l, song=song) for l in p["lines"])
            pending = []
            verses.append({"song": song, "verse": f"G{v}", "kind": "gitam", "meaning_te": meaning, "meaning_en": ""})
            for n, ln in enumerate(split_lines(cols, song), 1):
                lines.append(dict(ln, song=song, verse=f"G{v}", line=n))
        elif label.startswith("Sarga"):
            vid = "S" + label.split()[1]
            ls = [dict(l, verse=vid, line=n) for n, l in enumerate(split_lines(cols, 0), 1)]
            pending.append({"verse": {"song": None, "verse": vid, "kind": "sloka", "meaning_te": meaning, "meaning_en": ""}, "lines": ls})
        elif label.startswith(("Dhyanam", "Appendix")):
            pending = []
    return verses, lines


COMPILATION = "MTCehEEK8tA"


def yt_id(url):
    """Return (video_id, start_seconds) for a YouTube URL, else None."""
    from urllib.parse import parse_qs, urlparse
    if not url:
        return None
    u = urlparse(url)
    host, vid = u.netloc.lower(), None
    if "youtu.be" in host:
        vid = u.path.lstrip("/").split("/")[0]
    elif "youtube.com" in host and "music." not in host:
        vid = parse_qs(u.query).get("v", [None])[0]
    if not vid:
        return None
    t = parse_qs(u.query).get("t", ["0"])[0]
    return vid, int(re.sub(r"\D", "", t) or 0)


def read_index(path):
    """Songs (no, title, raga) and Videos rows (no, label, id, start, end) from the Index tab."""
    ws = openpyxl.load_workbook(path)["Index"]
    rows = [r for r in ws.iter_rows(min_row=2, max_row=40) if r[0].value is not None]
    starts = {}
    for r in rows:
        y = yt_id(r[8].hyperlink.target) if r[8].hyperlink else None
        if y:
            starts[int(float(r[0].value))] = y[1]
    ordered = sorted(starts)
    songs, videos = [], []
    for r in rows:
        no = int(float(r[0].value))
        songs.append((no, str(r[1].value).strip(), str(r[2].value or "").strip()))
        seen = set()

        def add(label, vid, start=0, end=None):
            if (vid, start) not in seen:
                seen.add((vid, start))
                videos.append((no, label, vid, start, end))

        comp = None
        if no in starts:
            nxt = [s for s in ordered if s > no]
            comp = (starts[no], starts[nxt[0]] if nxt else None)
        if r[3].hyperlink:
            y = yt_id(r[3].hyperlink.target)
            if y and y[0] == COMPILATION and comp:
                add("Saindhavi (Final pick)", COMPILATION, *comp)
            elif y:
                add("Final pick", y[0], y[1])
        if comp:
            add("Saindhavi (compilation)", COMPILATION, *comp)
        for c in (r[4], r[5], r[6]):
            if c.hyperlink:
                y = yt_id(c.hyperlink.target)
                if y and y[0] != COMPILATION:
                    add(re.sub(r"\s*\(YouTube[^)]*\)", "", str(c.value)), y[0], y[1])
    return songs, videos


README = [
    ("Tab", "Column", "What to put there"),
    ("Songs", "song_no / title / raga", "One row per song. Title is the opening phrase."),
    ("Verses", "song_no, verse", "G1, G2... = verses of the song; S1.1... = intro slokas. Must match the Lines tab."),
    ("Verses", "kind", "gitam or sloka."),
    ("Verses", "meaning_te / meaning_en", "The meaning of the WHOLE verse. Shown under its lines. Blank is fine."),
    ("Lines", "song_no, verse, line_no", "One row per line sung. Split long text into separate rows, one per line."),
    ("Lines", "devanagari / telugu / transliteration / telugu_phonetic", "The line in each script. Telugu is required."),
    ("Videos", "song_no, label, youtube_url", "One row per recording. Several per song are fine."),
    ("Videos", "start_sec / end_sec", "For a chapter inside a longer video. Blank end = play to the end."),
]


def write_workbook(verses, lines, songs, videos, out):
    from openpyxl.styles import Alignment, Font
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    def tab(name, header, rows, widths):
        ws = wb.create_sheet(name)
        ws.append(header)
        for r in rows:
            ws.append(list(r))
        for c in ws[1]:
            c.font = Font(bold=True)
        ws.freeze_panes = "A2"
        for i, w in enumerate(widths):
            ws.column_dimensions[chr(65 + i)].width = w
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        return ws

    tab("Songs", ["song_no", "title", "raga"], songs, [9, 34, 28])
    tab("Verses", ["song_no", "verse", "kind", "meaning_te", "meaning_en"],
        [(v["song"], v["verse"], v["kind"], v["meaning_te"], v["meaning_en"]) for v in verses],
        [9, 9, 9, 60, 60])
    tab("Lines", ["song_no", "verse", "line_no", "devanagari", "telugu", "transliteration", "telugu_phonetic"],
        [(l["song"], l["verse"], l["line"], l["dev"], l["te"], l["en"], l["tes"]) for l in lines],
        [9, 9, 9, 45, 45, 45, 45])
    tab("Videos", ["song_no", "label", "youtube_url", "start_sec", "end_sec"],
        [(n, lab, f"https://www.youtube.com/watch?v={vid}", s, e) for n, lab, vid, s, e in videos],
        [9, 30, 50, 10, 10])
    tab("Read me", list(README[0]), README[1:], [10, 40, 90])
    wb.save(out)


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "--write":
    verses, lines = convert(sys.argv[1])
    songs, videos = read_index(sys.argv[1])
    write_workbook(verses, lines, songs, videos, sys.argv[3])
    have = {l["song"] for l in lines}
    print(f"songs={len(songs)} verses={len(verses)} lines={len(lines)} videos={len(videos)}")
    print("songs with no lyrics:", [s[0] for s in songs if s[0] not in have])
    print("songs with no video:", [s[0] for s in songs if s[0] not in {v[0] for v in videos}])
    sys.exit(0)

if __name__ == "__main__":
    verses, lines = convert(sys.argv[1])
    want = {int(x) for x in sys.argv[2:]}
    print("VERSES  (song | verse | kind | meaning_te)")
    for v in verses:
        if not want or v["song"] in want:
            print(" ", v["song"], v["verse"], v["kind"], repr(v["meaning_te"][:30]))
    print("LINES   (song | verse | line | telugu)")
    for l in lines:
        if not want or l["song"] in want:
            print(" ", l["song"], l["verse"], l["line"], l["te"][:60])
    print(f"totals: verses={len(verses)} lines={len(lines)}")
