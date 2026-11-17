"""Regression tests for the sing-along page, run against a test clock instead of YouTube.

Run: python3 -I tests/test_page.py dist/index.html
"""
import json
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(sys.argv[1]).resolve().as_uri() + "?mock=1"
failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        failures.append(name)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    ctx = browser.new_context(accept_downloads=True)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    # Stand in for Google Fonts with the same Noto faces from local files (no network here).
    FONTS = pathlib.Path("/tmp/fontpkg")
    font_files = {
        "te.woff2": FONTS / "fontsource-noto-serif-telugu-5.3.0/files/noto-serif-telugu-telugu-400-normal.woff2",
        "dev.woff2": FONTS / "fontsource-noto-serif-devanagari-5.3.0/files/noto-serif-devanagari-devanagari-400-normal.woff2",
    }
    css = "".join(
        f"@font-face{{font-family:'{fam}';src:url(https://fonts.gstatic.com/{f}) format('woff2');font-weight:100 900}}"
        for fam, f in (("Noto Serif Telugu", "te.woff2"), ("Noto Serif Devanagari", "dev.woff2")))

    def fonts(route):
        url = route.request.url
        if "fonts.googleapis.com" in url:
            return route.fulfill(body=css, content_type="text/css")
        name = url.rsplit("/", 1)[-1]
        if name in font_files and font_files[name].exists():
            return route.fulfill(body=font_files[name].read_bytes(), content_type="font/woff2")
        return route.abort()

    page.route("https://fonts.googleapis.com/**", fonts)
    page.route("https://fonts.gstatic.com/**", fonts)
    page.goto(PAGE)
    page.wait_for_timeout(300)
    page.evaluate("document.getElementById('settings').open = true")

    # 1. loads with all songs and Telugu lyrics
    n_opts = page.locator("#songSel option").count()
    check("24 songs listed", n_opts == 24, n_opts)
    first = page.locator(".ln .t").first.inner_text()
    check("song 1 shows Telugu", first.startswith("ప్రలయ"), first)
    check("song 1 has 22 lines", page.locator(".ln").count() == 22)
    check("no-timing banner shown", page.locator("#noTiming").is_visible())
    check("missing-lyrics songs flagged", "(lyrics missing)" in page.locator("#songSel option").nth(15).inner_text())

    # 2. set timing: three lines, a break, a repeat by clicking, then undo
    page.click("#modeSync")
    check("sync bar visible", page.locator("#syncBar").is_visible())
    page.evaluate("__S.player.play()")
    for _ in range(3):
        page.wait_for_timeout(250)
        page.keyboard.press("Space")
    page.wait_for_timeout(200)
    page.keyboard.press("b")
    page.wait_for_timeout(200)
    page.locator(".ln").nth(1).click()  # singer repeats the refrain
    page.wait_for_timeout(200)
    page.keyboard.press("Space")  # next after g1 -> g2
    ev = page.evaluate("__S.timing.events")
    ids = [e[1] for e in ev]
    check("events recorded in order", ids == ["g0", "g1", "g2", "_", "g1", "g2"], ids)
    check("times increase", all(ev[i][0] < ev[i + 1][0] for i in range(len(ev) - 1)))
    page.keyboard.press("Backspace")
    check("undo removes last", [e[1] for e in page.evaluate("__S.timing.events")] == ["g0", "g1", "g2", "_", "g1"])

    # overwrite from an earlier point
    t_g2 = ev[2][0]
    page.evaluate(f"__S.player.seek({t_g2 - 0.01})")
    page.locator(".ln").nth(5).click()
    ids2 = [e[1] for e in page.evaluate("__S.timing.events")]
    check("marking earlier overwrites later marks", ids2 == ["g0", "g1", "g5"], ids2)
    page.keyboard.press("Backspace")
    page.evaluate(f"__S.player.seek({ev[3][0]})")
    page.keyboard.press("b"); page.wait_for_timeout(150)
    page.locator(".ln").nth(1).click()
    page.evaluate("__S.player.pause()")
    ev = page.evaluate("__S.timing.events")

    # 3. playback highlights the right line
    page.click("#modePlay")

    def cur_at(t):
        page.evaluate(f"__S.player.seek({t})")
        page.wait_for_timeout(80)
        el = page.locator(".ln.cur")
        return el.get_attribute("data-id") if el.count() else None

    check("before first mark: nothing highlighted", cur_at(max(0, ev[0][0] - 0.1)) is None)
    check("highlights g0", cur_at(ev[0][0] + 0.01) == "g0")
    check("highlights g1", cur_at(ev[1][0] + 0.01) == "g1")
    check("break clears highlight", cur_at(ev[2][0] + 0.01) is None)
    check("repeat highlights g1 again", cur_at(ev[3][0] + 0.01) == "g1")
    now_txt = page.locator("#now .main").inner_text()
    check("now card shows current line", now_txt.startswith("కేశవ"), now_txt)

    # offset nudge shifts timing
    page.click("#lateBtn")
    check("+¼s offset delays highlight", cur_at(ev[1][0] + 0.1) == "g0")
    page.click("#earlyBtn")

    # clicking a line in play mode seeks to it
    page.evaluate("__S.player.seek(0)")
    page.locator(".ln").nth(1).click()
    t = page.evaluate("__S.player.time()")
    check("click line seeks", abs(t - (ev[1][0] - 0.15)) < 0.3, t)
    page.evaluate("__S.player.pause()")

    # 4. script toggles
    page.click("#scriptSeg button[data-script=dev]")
    check("Devanagari script", page.locator(".ln .t").first.inner_text().startswith("प्रलय"))
    page.click("#scriptSeg button[data-script=te]")
    page.click("#splitBtn")
    check("word breaks", page.locator(".ln .t").first.inner_text().startswith("ప్రలయ పయోధి"))
    page.click("#splitBtn")
    page.click("#slokaBtn")
    check("opening slokas add lines", page.locator(".ln").count() > 22)
    check("highlight survives sloka toggle", cur_at(ev[0][0] + 0.01) == "g0")
    page.click("#slokaBtn")

    # 5. persistence across reload
    page.reload(); page.wait_for_timeout(300); page.evaluate("document.getElementById('settings').open = true")
    check("timing persists after reload", len(page.evaluate("__S.timing.events")) == len(ev))

    # 6. copy / paste round trip
    payload = page.evaluate("exportPayload()")
    page.click("#clearBtn"); page.click("#clearBtn")
    check("clear empties timing", page.evaluate("__S.timing.events.length") == 0)
    page.click("#importBtn"); page.fill("#importText", payload); page.click("#importOk")
    check("paste restores timing", len(page.evaluate("__S.timing.events")) == len(ev))

    # 7. .lrc download
    with page.expect_download() as dl:
        page.click("#lrcBtn")
    lrc = pathlib.Path(dl.value.path()).read_text(encoding="utf-8")
    check("lrc has timed Telugu lines", "]ప్రలయ" in lrc and lrc.count("\n[") >= len(ev), lrc[:120])

    # 8. compilation chapter: song 2 starts at 12:55 and stops at the next chapter
    page.select_option("#songSel", "gg2")
    src = page.evaluate("__S.src")
    check("song 2 uses Saindhavi chapter 775-1158", src["start"] == 775 and src["end"] == 1158, src)
    page.evaluate("__S.player.seek(1157.9); __S.player.play()")
    page.wait_for_timeout(400)
    check("stops at chapter end", not page.evaluate("__S.player.isPlaying()") and page.evaluate("__S.player.time()") < 1158)
    check("timing is per song", page.evaluate("__S.timing.events.length") == 0)

    # 9. add your own song
    page.click("#addSongBtn")
    page.fill("#songTitle", "Mandalinchu Rama")
    page.fill("#songUrl", "https://youtu.be/MwuFs0CQcFo?t=12")
    page.fill("#songLyrics", "# Verse 1\nఓసారి నన్ను మందలించు రామా\n\nఇంత వాడననచూ\n# Chorus\nకాల్చివాత పెట్టి, దండించు రామా")
    page.click("#songOk")
    check("custom song selected", page.evaluate("__S.song.title") == "Mandalinchu Rama")
    check("custom song lines", page.locator(".ln").count() == 3)
    check("custom start parsed", page.evaluate("__S.src.start") == 12)
    page.reload(); page.wait_for_timeout(300); page.evaluate("document.getElementById('settings').open = true")
    check("custom song persists", page.locator("#songSel option").count() == 25)

    # 10. no script errors throughout
    check("no page errors", not errors, errors)
    page.set_viewport_size({"width": 1280, "height": 860})
    page.select_option("#songSel", "gg1")
    page.evaluate(f"__S.player.seek({ev[1][0] + 0.01})"); page.wait_for_timeout(100)
    page.evaluate("document.getElementById('settings').open = false"); page.wait_for_timeout(300)
    page.screenshot(path="tests/desktop.png")
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(100)
    page.screenshot(path="tests/mobile.png")
    browser.close()

print(f"\n{len(failures)} failed" if failures else "\nAll tests passed")
sys.exit(1 if failures else 0)
