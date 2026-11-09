"""Render one "new in <version>" update story (1080x1920 JPEG), same look as the 0.16 story.

    python tools/update_story.py 0.19 "item one" "item two" ...  ->  stories/updates-0.19.jpg
"""
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE.parent / "stories"
F = HERE / "fonts"
M = HERE / "fonts/montserrat-latin-900-normal.woff2"
FACES = "".join(f"@font-face{{font-family:Poppins;font-weight:{w};src:url('file://{F}/poppins-latin-{w}-normal.woff2')}}"
                for w in (400, 500, 600, 700)) + f"@font-face{{font-family:Montserrat;font-weight:900;src:url('file://{M}')}}"
INK, YEL = "#0E0E12", "#FFC94A"

version, items = sys.argv[1], sys.argv[2:]
lis = "".join(f"<div style='display:flex;gap:28px;align-items:flex-start'><div style='flex:none;width:22px;height:22px;"
              f"border-radius:50%;background:{INK};margin-top:22px'></div><div>{t}</div></div>" for t in items)
html = f"""<!doctype html><html><head><meta charset='utf-8'><style>{FACES}body{{margin:0}}</style></head><body>
<div style="width:1080px;height:1920px;background-color:{YEL};color:{INK};font-family:Poppins;
box-sizing:border-box;padding:260px 90px 320px;display:flex;flex-direction:column;justify-content:space-between">
 <div style="display:flex;justify-content:space-between;font-size:30px;font-weight:600;letter-spacing:3px">
  <div>PEAKLIP</div><div style="opacity:.75">UPDATES</div></div>
 <div style="display:flex;flex-direction:column;gap:50px">
  <div style="font-family:Montserrat;font-weight:900;font-size:200px;line-height:.92;letter-spacing:-7px">new in<br>{version}.</div>
  <div style='display:flex;flex-direction:column;gap:28px;font-size:46px;line-height:1.33;font-weight:500'>{lis}</div>
  <div style="font-size:48px;line-height:1.38;font-weight:500">Your app updates itself from the bar at the top.</div>
 </div>
 <div style="font-size:34px;font-weight:600;opacity:.75">peaklip.com</div>
</div></body></html>"""
f = OUT / f"updates-{version}.html"
f.write_text(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get("CHROME") or None)
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"file://{f}")
    pg.evaluate("document.fonts.ready")
    over = pg.evaluate("document.body.firstElementChild.scrollHeight")
    pg.screenshot(path=str(OUT / f"updates-{version}.jpg"), type="jpeg", quality=94)
    b.close()
print("height", over, "->", OUT / f"updates-{version}.jpg")
