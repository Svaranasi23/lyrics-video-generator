// Unit tests for live/live_data.js. Run: node tests/test_live_data.js
const assert = require("assert");
const { parseCSV, buildData, ytId } = require("../live/live_data.js");

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

process.exit(fails ? 1 : 0);
