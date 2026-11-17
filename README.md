# Sing Along — Jayadeva Ashtapadi

A small web page that plays a song from YouTube and shows its lyrics underneath, in Telugu,
Devanagari or English, with an optional meaning for each verse. It works on a phone (video on top,
lyrics below) and on a computer. It is a learning tool.

The page reads its songs **live from a Google Sheet**, so changing a song, a video or a meaning
never needs a rebuild or a push: edit the Sheet, then refresh the page.

## Using the page
- Pick a **song**, a **recording** and a **language** at the top.
- A small **ⓘ** beside a verse opens its meaning. **All meanings** (in Display settings) opens them all.
- **Other YouTube link…** in the recording list adds a recording on that device only. To keep it for good,
  press **Copy added videos** and paste the rows under the last row of the Sheet's **Videos** tab.
- On a phone, the **⚙** button opens the settings, the speed control and **+ Your own song**.

## The Sheet (one per collection)
Four tabs, described on the Sheet's own **Read me** tab:

| Tab | One row is… |
|---|---|
| Songs | a song (number, title, raga) |
| Verses | a verse of a song, with its optional meaning (Telugu / English) |
| Lines | one line of lyrics, in each script |
| Videos | one recording of a song, with optional start and end seconds |

The Sheet must be published: **File → Share → Publish to web → Entire document → Web page**.

## Collections and the home page
`docs/collections.js` lists the collections shown on the home page. To add one: copy the template Sheet,
publish it, copy the spare entry in `collections.js`, fill in its name, published ID and four tab IDs, and
push that one file. Each collection keeps its own saved data in the browser.

## Publishing
GitHub Pages serves the `docs/` folder of `main`
(Settings → Pages → Deploy from branch → `main` → `/docs`). Only the page code is in Git; the lyrics live in
the Sheet. Everything in a published Sheet is readable by anyone with its link.

## Running it locally
```
cd docs && python3 -m http.server 8001      # then open http://localhost:8001
```

## Tests
`sh src/check.sh` (needs `python3 -m venv .venv && .venv/bin/pip install openpyxl`, and Node). It checks the Sheet
reader and that it matches the old Python build, using `src/data/gg-template.xlsx` (an export of the Sheet; not in Git).
