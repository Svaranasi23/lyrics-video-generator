/* Reads the standard template tabs (as CSV text) and returns the same data shape build.py produces.
   Works in the browser (window.LiveData) and in Node (module.exports) so it can be tested. */
(function (root) {
  "use strict";

  /** RFC 4180 CSV: quoted fields, doubled quotes, commas and newlines inside quotes. */
  function parseCSV(text) {
    const rows = []; let row = [], field = "", q = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; }
        else field += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(field); rows.push(row); row = []; field = "";
      } else field += c;
    }
    if (field !== "" || row.length) { row.push(field); rows.push(row); }
    return rows;
  }

  const cell = (v) => { const s = v == null ? "" : String(v).trim(); return s === "-" ? "" : s; };

  function toInt(v, what) {
    const n = parseFloat(v);
    if (!isFinite(n)) throw new Error(`${what}: expected a number, got "${v}"`);
    return Math.trunc(n);
  }

  function ytId(url) {
    if (!url) return null;
    let u; try { u = new URL(url); } catch (e) { return null; }
    const host = u.hostname.toLowerCase(); let vid = null;
    if (host.includes("youtu.be")) vid = u.pathname.replace(/^\//, "").split("/")[0];
    else if (host.includes("youtube.com") && !host.includes("music.")) vid = u.searchParams.get("v");
    if (!vid) return null;
    const t = u.searchParams.get("t") || "0";
    return { id: vid, start: parseInt(t.replace(/\D/g, "") || "0", 10) };
  }

  /** CSV text of one tab -> array of {header: value, _row}; fully blank rows skipped. */
  function rowsOf(csv) {
    const t = parseCSV(csv);
    if (!t.length) return [];
    const header = t[0].map(cell);
    const out = [];
    t.slice(1).forEach((r, i) => {
      const d = { _row: i + 2 };
      header.forEach((h, j) => { if (h) d[h] = r[j] == null ? "" : r[j]; });
      if (Object.keys(d).some((k) => k !== "_row" && cell(d[k]))) out.push(d);
    });
    return out;
  }

  function verseLabel(verse, kind) {
    const m = /^[GS]?(\d+(?:\.\d+)?)$/.exec(verse);
    const num = m ? m[1] : verse;
    if (kind === "sloka") return "Sarga " + num;
    return /^\d+$/.test(num) ? parseInt(num, 10) : num;
  }

  /** tabs = { songs, verses, lines, videos } as CSV text. */
  function buildData(tabs, title) {
    const songs = new Map();
    for (const r of rowsOf(tabs.songs)) {
      const no = toInt(r.song_no, `Songs row ${r._row} song_no`);
      songs.set(no, { no, title: cell(r.title), raga: cell(r.raga), sources: [], slokas: [], lines: [] });
    }
    const verses = new Map();  // "song|verse" -> info, insertion order = sheet order
    for (const r of rowsOf(tabs.verses)) {
      const no = toInt(r.song_no, `Verses row ${r._row} song_no`);
      if (!songs.has(no)) throw new Error(`Verses row ${r._row}: song ${no} is not in the Songs tab`);
      const verse = cell(r.verse), kind = (cell(r.kind) || "gitam").toLowerCase(), key = no + "|" + verse;
      if (verses.has(key)) throw new Error(`Verses row ${r._row}: duplicate verse ${verse} in song ${no}`);
      const mean = {};
      for (const k of ["te", "en"]) { const v = cell(r["meaning_" + k]); if (v) mean[k] = v; }
      verses.set(key, { no, verse, kind, mean, lines: [] });
    }
    for (const r of rowsOf(tabs.lines)) {
      const no = toInt(r.song_no, `Lines row ${r._row} song_no`), verse = cell(r.verse), key = no + "|" + verse;
      if (!verses.has(key)) throw new Error(`Lines row ${r._row}: verse ${verse} of song ${no} is not in the Verses tab`);
      const line = { dev: cell(r.devanagari), te: cell(r.telugu), en: cell(r.transliteration), tes: cell(r.telugu_phonetic) };
      if (!line.te) continue;  // Telugu is required; a row without it is ignored
      const order = cell(r.line_no) ? toInt(r.line_no, `Lines row ${r._row} line_no`) : r._row;
      verses.get(key).lines.push({ order, line });
    }
    for (const info of verses.values()) {
      const ls = info.lines.map((x, i) => ({ ...x, i })).sort((a, b) => a.order - b.order || a.i - b.i).map((x) => x.line);
      ls.forEach((l, i) => {
        l.v = verseLabel(info.verse, info.kind);
        if (i === 0 && Object.keys(info.mean).length) l.mean = info.mean;
      });
      songs.get(info.no)[info.kind === "sloka" ? "slokas" : "lines"].push(...ls);
    }
    for (const r of rowsOf(tabs.videos)) {
      const no = toInt(r.song_no, `Videos row ${r._row} song_no`);
      if (!songs.has(no)) throw new Error(`Videos row ${r._row}: song ${no} is not in the Songs tab`);
      const y = ytId(cell(r.youtube_url));
      if (!y) continue;  // blank or unrecognised link
      const start = cell(r.start_sec) ? toInt(r.start_sec, `Videos row ${r._row} start_sec`) : y.start;
      const end = cell(r.end_sec) ? toInt(r.end_sec, `Videos row ${r._row} end_sec`) : null;
      songs.get(no).sources.push({ label: cell(r.label) || "Video", id: y.id, start, end });
    }
    return { collection: title || "Collection", songs: [...songs.keys()].sort((a, b) => a - b).map((k) => songs.get(k)) };
  }

  const api = { parseCSV, rowsOf, buildData, ytId };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.LiveData = api;
})(typeof window !== "undefined" ? window : globalThis);
