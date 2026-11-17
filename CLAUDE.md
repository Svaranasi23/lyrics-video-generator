# Gita Govindam Sing-Along (lyric video app)

Static web page: embeds YouTube, highlights Ashtapadi lyrics line by line, timings set by the user.
Learning tool, not for publishing. No audio downloads (YouTube ToS). Full context: [docs/HANDOFF.md](docs/HANDOFF.md).

## Where things are
- Existing code (`src/build.py`, `src/template.html`, `src/tests/`, `src/check.sh`, `dist/`) is in the Drive folder
  "Lyric Video Generator" and has NOT been copied here yet. Copy it into this repo before working; this folder is
  the working home (Drive syncing a repo with `.git`/node_modules is a bad idea).
- Source of truth for lyrics: Google Sheet "8.2 Geethagovindam Ashtapadi" (tabs `Geethagovindam_raw`, `Index`).
  Export as .xlsx to `src/data/gg.xlsx` (gitignore it if the lyrics should stay private).
- Phase 1 research: `Sri_Gigs/LyricVideo/phase1-market-research.md`.

## How the user works
- Explicit Plan, Build, Test steps. Do not collapse them.
- Write and run unit tests yourself in the Build loop (`cd src && ./check.sh` after every change).
  Real YouTube player / mobile Safari testing is the user's (UAT); help debug from filtered logs.
- Token-conscious: targeted reads, no routine subagents.
- Ask before pushing, creating a repo, or changing repo visibility. GitHub Pages was approved 2026-11-16
  (suggested repo `gita-govindam-singalong`, public); confirm name and visibility before pushing.

## Test notes
`test_page.py` hard-codes `/usr/bin/google-chrome` and `/tmp/fontpkg`; on the Mac drop `executable_path`.

## Next steps
See HANDOFF.md "Next steps" (GitHub Pages, real-player test, songs 16/21/22 lyrics, bake timings, auto-timing, MP4 export).
