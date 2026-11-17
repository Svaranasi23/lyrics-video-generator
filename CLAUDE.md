# Sing Along: Jayadeva Ashtapadi (lyric page app)

Static web page: embeds YouTube and shows the lyrics (and optional verse meanings) underneath, read live from a Google Sheet.
Learning tool. No audio downloads (YouTube ToS). Full context: [docs/HANDOFF.md](docs/HANDOFF.md).

## Where things are
- The site is `docs/` (published by GitHub Pages from `main` `/docs`): `index.html` home page, `player.html` the
  player, `live_data.js` the Sheet reader, `collections.js` the list of collections (Sheet published IDs and tab ids).
- The page reads each collection's published Google Sheet live (tabs Songs, Verses, Lines, Videos). No build step
  for data. The Sheet is the master copy; `src/data/*.xlsx` exports are throwaway, used only by the tests.
- `src/build.py` (old Python build) stays as a cross-check; `src/tests/parity_live.py` proves the JS reader matches it.
  `src/convert_to_template.py` was the one-time converter from the old sheet.
- Design decisions: no per-line timing (just lyrics under the video), meanings optional per verse (tap to reveal),
  saved data in the browser is per collection, "Copy added videos" moves browser-added recordings into the Sheet.
- Phase 1 research: `Sri_Gigs/LyricVideo/phase1-market-research.md`. Older handoff: [docs/HANDOFF.md](docs/HANDOFF.md).

## How the user works
- Explicit Plan, Build, Test steps. Do not collapse them.
- Write and run unit tests yourself in the Build loop (`sh src/check.sh` after every change).
  Real YouTube player / mobile Safari testing is the user's (UAT); help debug from filtered logs.
- Token-conscious: targeted reads, no routine subagents.
- Ask before pushing or changing repo visibility. Repo: `Svaranasi23/lyrics-video-generator` (public, needed for free
  Pages). Pushing needs the user's own signed-in terminal (fine-grained token); the sandbox cannot push.

## Test notes
`sh src/check.sh` runs the unit tests and the parity check (uses `.venv` for openpyxl and Node for the reader).
Page behaviour is checked in a browser with `?fixture=fixture` (reads local CSVs from `docs/fixture/`, not in Git).

## Next steps
Publish (push, then Pages setting), try it on a phone, add lyrics for songs 16, 21 and 22 in the Sheet, then more
collections. Auto-timing and MP4 export from the old plan are dropped for now.
