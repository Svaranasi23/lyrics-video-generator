// Unit tests for docs/live_data.js. Run: node tests/test_live_data.js
const assert = require("assert");
const { parseCSV, buildData, ytId, addedVideoRows, toTSV, pickCollection, storageNS, scriptsIn } = require("../../docs/live_data.js");

let fails = 0;
function check(name, fn) {
  try { fn(); console.log("PASS " + name); } catch (e) { fails++; console.log("FAIL " + name + "  " + e.message); }
}

check("csv: plain rows", () => assert.deepStrictEqual(parseCSV("a,b\n1,2\n"), [["a", "b"], ["1", "2"]]));
check("csv: quotes, commas, doubled quotes, newline in a cell", () =>
  assert.deepStrictEqual(parseCSV('a,b\n"x, y","say ""hi""\nline2"\n'), [["a", "b"], ["x, y", 'say "hi"\nline2']]));
check("csv: CRLF and no trailing newline", () => assert.deepStrictEqual(parseCSV("a,b\r\n1,2"), [["a", "b"], ["1", "2"]]));
check("csv: Telugu and empty cells kept", () => assert.deepStrictEqual(parseCSV("t,u\nకేశవ,\n"), [["t", "u"], ["కేశవ", ""]]));
check("youtube ids", () => {
  assert.deepStrictEqual(ytId("https://www.youtube.com/watch?v=abc&list=RDabc&start_radio=1"), { id: "abc", start: 0 });
  assert.deepStrictEqual(ytId("https://youtu.be/xyz?t=5"), { id: "xyz", start: 5 });
  assert.strictEqual(ytId(""), null);
  assert.strictEqual(ytId("not a url"), null);
});

const T = {
  songs: "song_no,title,raga\n1,Alpha,Todi\n2,Beta,\n",
  verses: "song_no,verse,kind,meaning_te,meaning_en\n1,S1.1,sloka,,\n1,G1,gitam,అర్థం,meaning one\n1,G2,gitam,-,\n",
  lines: "song_no,verse,line_no,devanagari,telugu,transliteration,telugu_phonetic\n" +
    "1,G1,2,d2,t2,e2,p2\n1,G1,1,d1,t1,e1,p1\n1,S1.1,1,ds,ts,es,ps\n1,G2,1,d3,t3,e3,p3\n1,G2,2,,,,\n",
  videos: "song_no,label,youtube_url,start_sec,end_sec\n1,Final,https://www.youtube.com/watch?v=abc123,,\n" +
    "1,Chapter,https://www.youtube.com/watch?v=zzz999&t=30,,120\n1,Blank,,,\n2,Short,https://youtu.be/xyz?t=5,7,\n",
};
const d = buildData(T, "Test");
const [s1, s2] = d.songs;
check("lines ordered by line_no", () => assert.deepStrictEqual(s1.lines.slice(0, 2).map((l) => l.te), ["t1", "t2"]));
check("sloka separate, blank-Telugu row ignored", () => { assert.deepStrictEqual(s1.slokas.map((l) => l.te), ["ts"]); assert.strictEqual(s1.lines.length, 3); });
check("verse labels", () => { assert.strictEqual(s1.lines[0].v, 1); assert.strictEqual(s1.slokas[0].v, "Sarga 1.1"); });
check("meaning on first line only; blank and '-' publish nothing", () => {
  assert.deepStrictEqual(s1.lines[0].mean, { te: "అర్థం", en: "meaning one" });
  assert.ok(!("mean" in s1.lines[1]) && !("mean" in s1.lines[2]) && !("mean" in s1.slokas[0]));
});
check("videos: several, blank link skipped, start/end rules", () => {
  assert.deepStrictEqual(s1.sources.map((x) => x.label), ["Final", "Chapter"]);
  assert.strictEqual(s1.sources[1].start, 30); assert.strictEqual(s1.sources[1].end, 120); assert.strictEqual(s2.sources[0].start, 7);
});
check("song with no lines kept; raga blank", () => { assert.deepStrictEqual(s2.lines, []); assert.strictEqual(s2.raga, ""); });

const bad = (patch, text) => () => assert.throws(() => buildData({ ...T, ...patch }), (e) => e.message.includes(text));
check("error: line for unknown verse", bad({ lines: "song_no,verse,line_no,telugu\n1,G9,1,x\n" }, "G9"));
check("error: duplicate verse", bad({ verses: T.verses + "1,G1,gitam,,\n" }, "duplicate"));
check("error: video for unknown song", bad({ videos: "song_no,label,youtube_url\n9,x,https://youtu.be/a\n" }, "song 9"));
check("error: TBD in start_sec names the row", bad({ videos: "song_no,label,youtube_url,start_sec,end_sec\n2,x,https://youtu.be/a,TBD,TBD\n" }, "Videos row 2"));

const extras = { 2: [{ label: "Tab\there\nnewline", id: "abc", start: 90, end: null }], 5: [{ label: "Practice", id: "zzz", start: 0, end: 200 }] };
const rows = addedVideoRows([{ no: 1 }, { no: 2 }, { no: 5 }], (x) => extras[x.no]);
check("added videos: rows in Videos-tab column order", () => assert.deepStrictEqual(rows, [
  [2, "Tab here newline", "https://www.youtube.com/watch?v=abc", 90, ""], [5, "Practice", "https://www.youtube.com/watch?v=zzz", 0, 200]]));
check("added videos: songs with none give no rows; TSV pastes as columns", () => {
  assert.deepStrictEqual(addedVideoRows([{ no: 1 }], () => undefined), []);
  assert.strictEqual(toTSV(rows), "2\tTab here newline\thttps://www.youtube.com/watch?v=abc\t90\t\n5\tPractice\thttps://www.youtube.com/watch?v=zzz\t0\t200");
});

// A looser sheet, like "Traditional songs": no Verses tab, capitalised headers, only Telugu, sections labelled P1/C1.
const L2 = {
  songs: "Song_No,Title,Raga\n1,Aarti,\n2,Mangalam,Sindhu Bhairavi\n",
  verses: "",
  lines: 'song_no,verse,line_no,DEVANAGARI,Telugu,transliteration,telugu_phonetic\n' +
    '1,,P1,,"line a\nline b",,\n1,,C1,,"line c",,\n2,,c1,,"line d\nline e\nline f",,\n1,,P1,,"line g",,\n',
  videos: "song_no,label,youtube_url,start_sec,end_sec\n1,Short,https://youtube.com/shorts/ABC123?si=xyz,0,\n2,Embed,https://www.youtube.com/embed/EMB456,,\n",
};
const d2 = buildData(L2, "T");
check("loose sheet: capitalised headers and a missing Verses tab work", () => {
  assert.strictEqual(d2.songs.length, 2);
  assert.deepStrictEqual(d2.songs[0].lines.map((l) => l.te), ["line a\nline b", "line c", "line g"]);
});
check("loose sheet: P1/C1 labels (upper-cased), cell line breaks kept, sheet order", () => {
  assert.deepStrictEqual(d2.songs[0].lines.map((l) => l.v), ["P1", "C1", "P1"]);
  assert.strictEqual(d2.songs[1].lines[0].te, "line d\nline e\nline f");
  assert.strictEqual(d2.songs[1].lines[0].v, "C1");
});
check("loose sheet: named verse without a Verses tab still groups", () => {
  const d = buildData({ songs: "song_no,title\n1,A\n", verses: undefined, lines: "song_no,verse,line_no,telugu\n1,V1,2,two\n1,V1,1,one\n", videos: "" }, "T");
  assert.deepStrictEqual(d.songs[0].lines.map((l) => l.te), ["one", "two"]);
});
check("loose sheet: missing videos tab is fine; line for an unknown song errors", () => {
  assert.deepStrictEqual(buildData({ songs: "song_no,title\n1,A\n", lines: "", verses: "", videos: undefined }, "T").songs[0].sources, []);
  assert.throws(() => buildData({ songs: "song_no,title\n1,A\n", lines: "song_no,telugu\n9,x\n" }, "T"), (e) => e.message.includes("song 9"));
});
check("youtube: Shorts and embed links", () => {
  assert.deepStrictEqual(d2.songs[0].sources.map((x) => x.id), ["ABC123"]);
  assert.deepStrictEqual(d2.songs[1].sources.map((x) => x.id), ["EMB456"]);
  assert.strictEqual(ytId("https://www.youtube.com/live/LIVE789").id, "LIVE789");
});
check("scripts: only the ones with text are reported", () => {
  assert.deepStrictEqual(scriptsIn(d2.songs), { te: true, dev: false, en: false, tes: false });
  assert.deepStrictEqual(scriptsIn(d.songs), { te: true, dev: true, en: true, tes: true });
});

const COLS = [{ slug: "gita-govindam", title: "G" }, { slug: "kirtanas", title: "K" }];
check("collections: pick by slug, default first, unknown falls back", () => {
  assert.strictEqual(pickCollection(COLS, "kirtanas").title, "K");
  assert.strictEqual(pickCollection(COLS, null).title, "G");
  assert.strictEqual(pickCollection(COLS, "nope").title, "G");
  assert.strictEqual(pickCollection([], "x"), null);
});
check("collections: first keeps old storage keys, others get a prefix", () => {
  assert.strictEqual(storageNS(COLS, COLS[0]), "");
  assert.strictEqual(storageNS(COLS, COLS[1]), "kirtanas:");
  assert.strictEqual(storageNS([], null), "");
});

process.exit(fails ? 1 : 0);
