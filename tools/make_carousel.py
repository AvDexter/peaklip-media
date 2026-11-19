"""Render a Peaklip carousel (1080x1350 JPEG slides) from a small spec.

    python tools/make_carousel.py carousels/howto-01.json   ->  images/howto-01/1.jpg, 2.jpg, ...

Spec: {"id": "howto-01", "slides": [
  {"kind": "cover", "kicker": "HOW TO", "title": "3 hours of stream. 5 clips.", "sub": "The whole process, in 5 steps."},
  {"kind": "step", "n": 1, "title": "Import your stream", "text": "…", "visual": "import|moments|look|approve|post"},
  {"kind": "cta", "title": "Try it free for 3 days.", "sub": "Link in bio."}]}
Look: dark #0E0E12 / paper #F2F0EB, yellow #FFC94A, Poppins + Montserrat Black. Every slide carries "swipe" and a page count.
"""
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ROOT = HERE.parent
F = HERE / "fonts"
FACES = "".join(f"@font-face{{font-family:Poppins;font-weight:{w};src:url('file://{F}/poppins-latin-{w}-normal.woff2')}}"
                for w in (400, 500, 600, 700)) + \
    f"@font-face{{font-family:Montserrat;font-weight:900;src:url('file://{F}/montserrat-latin-900-normal.woff2')}}"
INK, PAPER, YEL = "#0E0E12", "#F2F0EB", "#FFC94A"
CARD = "#18181E"

CSS = f"""{FACES}
*{{box-sizing:border-box}} body{{margin:0}}
.s{{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Poppins;padding:90px 84px;display:flex;flex-direction:column}}
.dark{{background:{INK};color:{PAPER}}} .paper{{background:{PAPER};color:{INK}}} .yel{{background:{YEL};color:{INK}}}
.top{{display:flex;justify-content:space-between;font-size:28px;font-weight:600;letter-spacing:3px}}
.top .r{{opacity:.6}}
.big{{font-family:Montserrat;font-weight:900;letter-spacing:-4px;line-height:.98}}
.body{{flex:1;display:flex;flex-direction:column;justify-content:center;gap:34px}}
.txt{{font-size:42px;line-height:1.36;font-weight:500;max-width:860px}}
.dark .txt{{opacity:.82}}
.num{{font-family:Montserrat;font-weight:900;font-size:150px;line-height:1;color:{YEL}}}
.paper .num{{color:{INK};background:{YEL};display:inline-block;padding:0 34px;border-radius:30px;font-size:120px;line-height:1.22;width:max-content}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:600}}
.dots{{display:flex;gap:12px}} .dots i{{width:14px;height:14px;border-radius:50%;background:currentColor;opacity:.25}} .dots i.on{{opacity:1;background:{YEL}}}
.paper .dots i.on{{background:{INK}}} .yel .dots i.on{{background:{INK}}}
.vis{{height:300px;display:flex;align-items:center}}
.card{{background:{CARD};color:{PAPER};border-radius:28px;padding:26px 30px;font-size:30px;font-weight:600}}
.paper .card{{box-shadow:0 18px 40px rgba(14,14,18,.18)}}
.row{{display:flex;align-items:center;gap:20px}}
.chip{{border-radius:99px;padding:6px 20px;font-size:24px;font-weight:700;background:{YEL};color:{INK}}}
.chip.g{{background:#3a3a44;color:{PAPER}}}
.bar{{height:14px;border-radius:7px;background:#3a3a44;position:relative;width:100%}}
.bar b{{position:absolute;top:-6px;height:26px;border-radius:7px;background:{YEL}}}
.clip{{width:150px;height:260px;border-radius:22px;background:linear-gradient(160deg,#2a2a34,#14141a);border:3px solid #2e2e38;position:relative}}
.clip.on{{border-color:{YEL}}} .clip:after{{content:"";position:absolute;left:18px;right:18px;bottom:30px;height:12px;border-radius:6px;background:{PAPER};opacity:.85}}
"""

def visual(key):
    if key == "import":
        return """<div class=card style="width:100%"><div class=row style="justify-content:space-between"><span>Friday stream.mp4</span><span class=chip>3:02:41</span></div>
        <div class=bar style="margin-top:26px"><b style="left:0;width:100%;background:#4a4a56;opacity:.6"></b></div></div>"""
    if key == "moments":
        rows = "".join(f"<div class=row style='justify-content:space-between;padding:10px 0'><span>{t}</span><span class='chip{c}'>{v}</span></div>"
                       for t, v, c in (("1:12:08", "Great", ""), ("2:03:55", "Great", ""), ("0:41:20", "Good", " g")))
        return f"<div class=card style='width:100%'>{rows}</div>"
    if key == "look":
        return "<div class=row style='gap:26px'>" + "".join(f"<div class='clip{' on' if i == 1 else ''}'></div>" for i in range(3)) + "</div>"
    if key == "approve":
        return f"""<div class=card style="width:100%"><div class=row style="justify-content:space-between"><span>Clip 2 of 5</span><span class=chip>Approve</span></div>
        <div class=bar style="margin-top:26px"><b style="left:18%;width:30%"></b></div></div>"""
    if key == "post":
        return "<div class=row style='gap:22px'>" + "".join(f"<div class=card style='font-size:34px;padding:30px 36px'>{n}</div>" for n in ("YouTube", "Instagram", "TikTok")) + "</div>"
    return ""

def slide(i, n, s):
    dots = "<div class=dots>" + "".join(f"<i class='{'on' if k == i else ''}'></i>" for k in range(n)) + "</div>"
    swipe = "<span style='opacity:.6'>swipe →</span>" if i < n - 1 else "<span style='opacity:.6'>peaklip.com</span>"
    foot = f"<div class=foot>{swipe}{dots}</div>"
    top = f"<div class=top><div>PEAKLIP</div><div class=r>{s.get('tag', '')}</div></div>"
    k = s["kind"]
    if k == "cover":
        body = (f"<div class=body><div style='font-size:34px;font-weight:700;letter-spacing:4px;color:{YEL}'>{s.get('kicker', '')}</div>"
                f"<div class=big style='font-size:118px'>{s['title']}</div><div class=txt>{s.get('sub', '')}</div></div>")
        cls = "dark"
    elif k == "step":
        body = (f"<div class=body><div class=num>{s['n']}</div><div class=big style='font-size:96px'>{s['title']}</div>"
                f"<div class=txt>{s['text']}</div><div class=vis>{visual(s.get('visual', ''))}</div></div>")
        cls = "paper" if s["n"] % 2 else "dark"
    else:
        body = (f"<div class=body><div class=big style='font-size:128px'>{s['title']}</div><div class=txt style='font-weight:600'>{s.get('sub', '')}</div></div>")
        cls = "yel"
    return f"<div class='s {cls}'>{top}{body}{foot}</div>"

def main(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    slides = spec["slides"]
    out = ROOT / "images" / spec["id"]
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROME") or None)
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides):
            html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{slide(i, len(slides), s)}</body></html>"
            f = out / f"_{i + 1}.html"
            f.write_text(html)
            pg.goto(f"file://{f}")
            pg.evaluate("document.fonts.ready")
            over = pg.evaluate("document.querySelector('.s').scrollHeight")
            pg.screenshot(path=str(out / f"{i + 1}.jpg"), type="jpeg", quality=94)
            f.unlink()
            print(i + 1, "overflow!" if over > 1350 else "ok")
        b.close()

if __name__ == "__main__":
    main(sys.argv[1])
