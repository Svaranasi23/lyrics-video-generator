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
    const host = u.hostname.toLowerCase(), parts = u.pathname.split("/").filter(Boolean); let vid = null;
    if (host.includes("youtu.be")) vid = parts[0];
    else if (host.includes("youtube.com") && !host.includes("music."))
      vid = u.searchParams.get("v") || (["shorts", "embed", "live", "v"].includes(parts[0]) ? parts[1] : null);
    if (!vid) return null;
    const t = u.searchParams.get("t") || "0";
    return { id: vid, start: parseInt(t.replace(/\D/g, "") || "0", 10) };
  }

  /** CSV text of one tab -> array of {header: value, _row}; fully blank rows skipped. */
  const norm = (h) => String(h == null ? "" : h).trim().toLowerCase().replace(/[\s-]+/g, "_");
  function rowsOf(csv) {
    const t = parseCSV(csv || "");
    if (!t.length) return [];
    const header = t[0].map(norm);
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
      songs.set(no, { no, title: cell(r.title), raga: cell(r.raga), writer: cell(r.writer), sources: [], slokas: [], lines: [] });
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
    const strict = verses.size > 0;  // a Verses tab with rows means every line's verse must be listed there
    for (const r of rowsOf(tabs.lines)) {
      const no = toInt(r.song_no, `Lines row ${r._row} song_no`), verse = cell(r.verse);
      if (!songs.has(no)) throw new Error(`Lines row ${r._row}: song ${no} is not in the Songs tab`);
      const lineNo = cell(r.line_no), numeric = /^\d+(\.\d+)?$/.test(lineNo);
      let key;
      if (verse) {
        key = no + "|" + verse;
        if (!verses.has(key)) {
          if (strict) throw new Error(`Lines row ${r._row}: verse ${verse} of song ${no} is not in the Verses tab`);
          verses.set(key, { no, verse, kind: "gitam", mean: {}, lines: [] });
        }
      } else {  // no verse: each row is its own section, labelled by line_no when that is text (P1, C1...)
        key = no + "|#row" + r._row;
        verses.set(key, { no, verse: "", label: lineNo && !numeric ? lineNo.toUpperCase() : "", kind: "gitam", mean: {}, lines: [] });
      }
      // A cell may hold several lines (Enter inside the cell); the page shows them as typed.
      const line = { dev: cell(r.devanagari), te: cell(r.telugu), en: cell(r.transliteration), tes: cell(r.telugu_phonetic) };
      const order = lineNo && numeric ? toInt(lineNo, `Lines row ${r._row} line_no`) : r._row;
      const info = verses.get(key);  // optional meaning_te / meaning_en on a Lines row (for sheets with no Verses tab)
      for (const k of ["te", "en"]) { const m = cell(r["meaning_" + k]); if (m && !info.mean[k]) info.mean[k] = m; }
      if (line.te) info.lines.push({ order, line });  // Telugu is required; a row without it is ignored
    }
    for (const info of verses.values()) {
      const ls = info.lines.map((x, i) => ({ ...x, i })).sort((a, b) => a.order - b.order || a.i - b.i).map((x) => x.line);
      ls.forEach((l, i) => {
        l.v = info.label !== undefined ? info.label : verseLabel(info.verse, info.kind);
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

  /** Recordings added on this device -> rows in the Videos tab's column order. extraFor(song) returns [{label,id,start,end}]. */
  function addedVideoRows(songs, extraFor) {
    const clean = (v) => String(v == null ? "" : v).replace(/[\t\r\n]+/g, " ").trim();
    const rows = [];
    for (const s of songs) for (const v of extraFor(s) || [])
      rows.push([s.no, clean(v.label), "https://www.youtube.com/watch?v=" + v.id, v.start || 0, v.end == null ? "" : v.end]);
    return rows;
  }
  const toTSV = (rows) => rows.map((r) => r.join("\t")).join("\n");

  /** The collection a page shows: the one named by slug, else the first. */
  function pickCollection(list, slug) { return list.find((c) => c.slug === slug) || list[0] || null; }
  /** Prefix for a collection's saved data. The first collection keeps the original (empty) prefix. */
  function storageNS(list, c) { return !c || (list.length && c.slug === list[0].slug) ? "" : c.slug + ":"; }

  /** The meaning to show for the chosen script: Telugu shows meaning_te, English (and Devanagari) show meaning_en.
      If that one is blank the other is shown, so a meaning is never hidden. */
  function pickMeaning(mean, script) {
    const order = script === "te" ? ["te", "en"] : ["en", "te"];
    const k = order.find((x) => mean && mean[x]);
    return k ? { lang: k, text: mean[k] } : null;
  }

  /** Which scripts have any text, so the page can hide the ones a collection doesn't have. */
  function scriptsIn(songs) {
    const has = { te: false, dev: false, en: false, tes: false };
    for (const s of songs) for (const l of s.lines.concat(s.slokas)) for (const k of Object.keys(has)) if (l[k]) has[k] = true;
    return has;
  }

  const api = { parseCSV, rowsOf, buildData, ytId, addedVideoRows, toTSV, pickCollection, storageNS, scriptsIn, pickMeaning };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.LiveData = api;
})(typeof window !== "undefined" ? window : globalThis);
