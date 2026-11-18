# Session notes (as of 2026-11-18, main = 121aa76 plus this file)

Latest state of Sing Along. Read this after a /clear. Project rules are in CLAUDE.md and README.md.

## Live and verified
- Song dropdown shows `no · title - writer` (optional `writer` column on the Songs tab). Ashtapadi Sheet has Jayadeva on all 24 songs; Lalitha Sangeetham Sheet already had a Writer column.
- Language dropdown follows the selected song (scripts a song has no text for are hidden; saved choice kept).
- Speed buttons: 0.25, 0.5, 0.75, 1, 1.25, 1.5 (0.5 was my reading of the user's "0.1").
- 4 collections in docs/collections.js, all with tab ids songs 1233158892, verses 1471833179, lines 924686161, videos 1420763163:
  jayadeva-ashtapadi; traditional-songs (slug kept, now titled "Lalitha Sangeetham" so saved data carries over);
  annamayya-songs (3 songs); harathi-songs (2 songs).
- Shared scripts are at `?v=7` in index.html and player.html. Bump when collections.js or live_data.js changes.
- `sh src/check.sh` passes (0 failures).

## Open items
- User to check on a phone: do six speed buttons fit on one row? If not, make them a dropdown.
- Telugu names are my guesses (లలిత సంగీతం, అన్నమయ్య కీర్తనలు, హారతి పాటలు). User wrote "Hangala Harathi"; Sheet title is "Harathi songs", so title is "Harathi Songs".
- Harathi Sheet writer column says "Mangala harati" (a song type, not a person); user may want to change it.
- Missing lyrics: Ashtapadi songs 16, 21, 22. No meaning_te / meaning_en columns yet on the Lalitha Sangeetham Sheet. Two of its videos cannot be embedded (owner's choice).
- User should delete the old GitHub token if not done.
- Parked (needs user's go-ahead): "Listen on YouTube" link in Lyrics-only mode, or a small visible video tile, for audio without full video.

## Working notes
- Sandbox cannot push, run servers, or reach docs.google.com from the shell. The user pushes from their own terminal.
- To read a published Sheet's tab ids: open its `.../pubhtml` in the browser pane and read the tab list from the page source.
- GitHub Pages takes about 10 minutes to update after a push. Test on the live site in the browser pane.
