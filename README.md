# Gita Govindam — Sing Along

A single web page (`index.html`) that plays each Ashtapadi from YouTube and shows its
lyrics in Telugu, Devanagari or English, highlighting each line as it is sung.

## Opening it

YouTube won't play inside a page opened by double-clicking the file, so open it
through a web address:

- **On your Mac, from this folder:** open Terminal, then run
  `cd "<this folder>"` and `python3 -m http.server 8000`,
  and go to <http://localhost:8000> in your browser. Press Ctrl+C in Terminal to stop.
- **Or from a hosted copy**, if one has been set up.

## Using it

1. Pick a song and a rendition at the top. Songs 1 and 3 open your Final pick; the rest open their chapter
   of the Saindhavi compilation and stop at the end of that chapter.
2. **First time for a rendition:** choose **Set timing**, press play, and tap
   **Space** (or *Next line*) the moment each line starts. If the singer repeats an
   earlier line, click that line in the list. **B** marks a music break; **Backspace** undoes.
3. Switch to **Sing along**. The current line is highlighted and shown large.
   Click any line to jump there; *Loop line* repeats it; *0.75×* slows it down.
4. **Display & timing tools:** script, word breaks (pada-chheda), transliteration,
   opening slokas, text size, ±¼s timing nudge, copy/paste timing, download `.lrc`.

Timing is saved in the browser you used. Use **Copy timing** to back it up or move it
to another device or browser (**Paste timing** there).

Songs 16, 21 and 22 have no lyrics in the spreadsheet yet. **+ Your own song** works
for any YouTube video and any lyrics.

Built from `8.2 Geethagovindam Ashtapadi` (tabs *Geethagovindam_raw* and *Index*).
