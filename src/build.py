"""Build the sing-along page from the standard template workbook.

Usage: python build.py data/gg-template.xlsx template.html dist/index.html [collection title]

The workbook has tabs Songs, Verses, Lines, Videos (see its "Read me" tab).
Meanings are optional per verse: a blank cell publishes nothing.
"""
import json
import os
import re
import sys
from urllib.parse import parse_qs, urlparse

import openpyxl

DEFAULT_TITLE = "Gita Govindam — Ashtapadi"


def cell(v):
    """Cell text, or '' for blank (None, '', '-')."""
    s = "" if v is None else str(v).strip()
    return "" if s == "-" else s


def to_int(v, what):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        raise ValueError(f"{what}: expected a number, got {v!r}")


def yt_id(url):
    """Return (video_id, start_seconds) for a YouTube URL, else None."""
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


def rows(ws):
    """Data rows as dicts keyed by the header row; skips fully blank rows."""
    it = ws.iter_rows(values_only=True)
    header = [cell(h) for h in next(it)]
    for n, r in enumerate(it, 2):
        d = {h: r[i] if i < len(r) else None for i, h in enumerate(header) if h}
        if any(cell(v) for v in d.values()):
            d["_row"] = n
            yield d


def verse_label(verse, kind):
    """What the page shows beside a verse: a number for gitam verses, 'Sarga 1.1' for slokas."""
    m = re.fullmatch(r"[GS]?(\d+(?:\.\d+)?)", verse)
    num = m.group(1) if m else verse
    if kind == "sloka":
        return f"Sarga {num}"
    return int(num) if num.isdigit() else num


def build_data(path, title=DEFAULT_TITLE):
    wb = openpyxl.load_workbook(path, data_only=True)
    for tab in ("Songs", "Verses", "Lines", "Videos"):
        if tab not in wb.sheetnames:
            raise ValueError(f"missing tab: {tab}")

    songs = {}
    for r in rows(wb["Songs"]):
        no = to_int(r.get("song_no"), f"Songs row {r['_row']} song_no")
        songs[no] = {"no": no, "title": cell(r.get("title")), "raga": cell(r.get("raga")),
                     "writer": cell(r.get("writer")),
                     "sources": [], "slokas": [], "lines": []}

    verses = {}  # (song, verse) -> info, in sheet order
    for r in rows(wb["Verses"]):
        no = to_int(r.get("song_no"), f"Verses row {r['_row']} song_no")
        if no not in songs:
            raise ValueError(f"Verses row {r['_row']}: song {no} is not in the Songs tab")
        verse, kind = cell(r.get("verse")), (cell(r.get("kind")) or "gitam").lower()
        if (no, verse) in verses:
            raise ValueError(f"Verses row {r['_row']}: duplicate verse {verse} in song {no}")
        mean = {k: cell(r.get(f"meaning_{k}")) for k in ("te", "en")}
        verses[(no, verse)] = {"kind": kind, "mean": {k: v for k, v in mean.items() if v}, "lines": []}

    for r in rows(wb["Lines"]):
        no = to_int(r.get("song_no"), f"Lines row {r['_row']} song_no")
        verse = cell(r.get("verse"))
        if (no, verse) not in verses:
            raise ValueError(f"Lines row {r['_row']}: verse {verse} of song {no} is not in the Verses tab")
        line = {"dev": cell(r.get("devanagari")), "te": cell(r.get("telugu")),
                "en": cell(r.get("transliteration")), "tes": cell(r.get("telugu_phonetic"))}
        if not line["te"]:
            continue  # Telugu is required; a row without it is ignored
        order = to_int(r.get("line_no"), f"Lines row {r['_row']} line_no") if cell(r.get("line_no")) else r["_row"]
        verses[(no, verse)]["lines"].append((order, line))

    for (no, verse), info in verses.items():
        ls = [l for _, l in sorted(info["lines"], key=lambda x: x[0])]
        for i, l in enumerate(ls):
            l["v"] = verse_label(verse, info["kind"])
            if i == 0 and info["mean"]:
                l["mean"] = info["mean"]  # meaning rides on the first line of its verse
        songs[no]["slokas" if info["kind"] == "sloka" else "lines"].extend(ls)

    for r in rows(wb["Videos"]):
        no = to_int(r.get("song_no"), f"Videos row {r['_row']} song_no")
        if no not in songs:
            raise ValueError(f"Videos row {r['_row']}: song {no} is not in the Songs tab")
        y = yt_id(cell(r.get("youtube_url")))
        if not y:
            continue  # blank or unrecognised link
        start = to_int(r["start_sec"], "start_sec") if cell(r.get("start_sec")) else y[1]
        end = to_int(r["end_sec"], "end_sec") if cell(r.get("end_sec")) else None
        songs[no]["sources"].append({"label": cell(r.get("label")) or "Video", "id": y[0],
                                     "start": start, "end": end})

    return {"collection": title, "songs": [songs[k] for k in sorted(songs)]}


def render(data, template_path, out_path):
    html = open(template_path, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("/*__DATA__*/null", payload)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    xlsx, template, out = sys.argv[1:4]
    data = build_data(xlsx, sys.argv[4] if len(sys.argv) > 4 else DEFAULT_TITLE)
    render(data, template, out)
    s = data["songs"]
    print(f"songs={len(s)} lines={sum(len(x['lines']) for x in s)} "
          f"meanings={sum(1 for x in s for l in x['lines'] + x['slokas'] if 'mean' in l)} "
          f"missing_lyrics={[x['no'] for x in s if not x['lines']]} "
          f"no_video={[x['no'] for x in s if not x['sources']]}")
