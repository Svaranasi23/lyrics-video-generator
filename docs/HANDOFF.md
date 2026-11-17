# Handoff — Gita Govindam Sing-Along (Lyric Video app)

Written 2026-11-16 from a Claude chat session, for continuing in Claude Code.
Copied from Drive: "Lyric Video Generator/HANDOFF.md" (file id 16l-IC7ma1NZQMam4BwLxfPaCwb1Zl4AO).
Project context: Sri's App Factory. Phase 1 research is at
`Sri_Gigs/LyricVideo/phase1-market-research.md` and in the Claude Project as
`claude/lyric-video-phase1-market-research.md`.

## What this is
A single static web page that plays each Gita Govindam Ashtapadi from YouTube and
highlights the lyrics line by line as they're sung. It's for learning the songs, not
publishing. Sri chose "Option 1": no audio downloads. It embeds YouTube and syncs timed
lyrics on top, which avoids YouTube's terms-of-service problem with downloading.

## Files (all in the Drive folder "Lyric Video Generator")
| File | Purpose |
|---|---|
| `8.2 Geethagovindam Ashtapadi` (Google Sheet shortcut) | **Source of truth.** Tab `Geethagovindam_raw` = lyrics; tab `Index` = song list + YouTube links. |
| `src/build.py` | Reads the sheet (exported as .xlsx) → writes `dist/index.html` with the data embedded. |
| `src/template.html` | The page itself (HTML/CSS/JS, no framework). `/*__DATA__*/null` is replaced by the build. |
| `src/tests/test_page.py` | 34 Playwright regression checks using a stand-in clock (`?mock=1`) instead of YouTube. |
| `src/check.sh` | Rebuild + run all tests. **Run after every change.** |
| `index.html`, `README.md` | Current built page + user instructions (copy of `dist/`). |

## How to rebuild and test
1. Export the Google Sheet as .xlsx to `src/data/gg.xlsx`. From Drive for desktop:
   File → Download → .xlsx in Sheets, or use the Drive/Sheets API.
2. `pip install openpyxl playwright && playwright install chromium`
3. `cd src && ./check.sh`
   - `test_page.py` currently hard-codes `executable_path="/usr/bin/google-chrome"`
     and loads Noto fonts from `/tmp/fontpkg`. On the Mac, drop the
     `executable_path` argument and let the font route fall back (it aborts font
     requests if the files are missing, so tests still pass).

## How the data is parsed (build.py)
- Lyrics: rows labelled `Gitam N.V` belong to song N, verse V. Each cell is split into
  lines on `~`. Columns: D=Devanagari, E=Telugu, F=English transliteration,
  G=Telugu with word breaks. Song 1 has no `~`, so it's split before "కేశవ".
  Trailing verse numbers and `!` are stripped.
- `Sarga x.y` rows just before a song become that song's optional "Opening slokas".
- Index: column D = "Final" pick, E/F/G = other renditions, I = chapter timestamp
  link in the Saindhavi compilation (video `MTCehEEK8tA`). The chapter end = the
  next song's start, so playback stops at the chapter boundary.
- **Missing lyrics: songs 16, 21, 22** have no `Gitam` rows in the sheet. They show
  as "(lyrics missing)".

## Page features (template.html)
- Sing along mode: highlight + large "now" line, click a line to seek, Loop line,
  ◀/▶ line, 0.75× speed, ±¼s timing nudge.
- Set timing mode: Space = next line, click a line = mark that line (for repeats),
  B = music break, Backspace = undo. Marking at time t overwrites all later marks.
- Timing is stored in localStorage, keyed by song + video + start time. Copy/Paste
  timing (JSON) moves it between devices. Download .lrc.
- "+ Your own song": any YouTube link + pasted lyrics (`#` lines = headings).
- Scripts: Telugu / Devanagari / English, word breaks, transliteration toggle.
- `DATA.timings` (baked-in timings) is supported but empty. Once Sri has set
  timings, they can be baked in so every device gets them (see Next steps).

## Next steps
1. **Put it on GitHub Pages (Sri approved, 2026-11-16).** Create a repo (suggested
   `gita-govindam-singalong`, public, since Pages needs public on a free plan), commit
   `src/` + `dist/`, publish `dist/` via Pages, and send Sri the link. The chat session
   couldn't do this because GitHub wasn't connected there.
   Ask Sri before pushing if the repo name or visibility is unclear.
2. **Test against the real YouTube player** (localhost or Pages). Not yet done:
   all tests so far used the stand-in clock. Things to check: the compilation
   chapters start and stop correctly, the speed control, mobile Safari.
3. Rebuild once Sri adds lyrics for songs 16, 21 and 22.
4. Optional: bake Sri's timings into the build (import pasted "Copy timing" JSON
   into `DATA.timings`) so they work on every device without pasting.
5. Later, from the original idea: auto-timing (Demucs vocal isolation + MMS/WhisperX
   forced alignment) and exporting a static lyric video MP4 (ffmpeg + libass with
   HarfBuzz, Noto Serif Telugu). See the Phase 1 doc.
