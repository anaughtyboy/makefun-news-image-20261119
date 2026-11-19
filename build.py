#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261119.

Layout: 1024x1024 newspaper front page. Masthead names the day;
six story blocks (2x3 grid), each with a picture panel, a kicker,
a headline and a one-line summary. Four panels are AI-generated
illustrations made in this session (assets/*.webp, no text in them);
two panels (GTA VI skyline, Voyager 1) are drawn with PIL below.
All story facts were verified against news reports of 19 Nov 2026.
"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(REPO, "assets")

W, H = 1024, 1024
NAVY = (15, 42, 74)
NAVY_DARK = (10, 30, 54)
GOLD = (201, 162, 39)
PAPER = (250, 247, 240)
INK = (20, 20, 20)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_gta_panel(size):
    """Neon Vice City-style skyline at dusk, drawn with PIL."""
    s = size
    img = Image.new("RGB", (s, s), (24, 8, 44))
    d = ImageDraw.Draw(img)
    # sunset gradient bands
    bands = [(58, 16, 72), (122, 32, 86), (214, 72, 96), (255, 122, 89),
             (255, 178, 102), (255, 214, 140)]
    bh = s // 2 // len(bands)
    for i, c in enumerate(bands):
        d.rectangle([0, i * bh, s, (i + 1) * bh], fill=c)
    # sun
    d.ellipse([s * 0.36, s * 0.10, s * 0.64, s * 0.38], fill=(255, 236, 170))
    # skyline, back row
    import random
    rnd = random.Random(7)
    x = 0
    while x < s:
        bw = rnd.randint(26, 54)
        bhgt = rnd.randint(s // 5, s // 2)
        d.rectangle([x, s - bhgt - s // 4, x + bw, s], fill=(30, 12, 52))
        x += bw + rnd.randint(2, 10)
    # skyline, front row with lit windows
    x = 0
    while x < s:
        bw = rnd.randint(34, 62)
        bhgt = rnd.randint(s // 8, s // 3)
        top = s - bhgt
        d.rectangle([x, top, x + bw, s], fill=(16, 8, 34))
        for wy in range(top + 8, s - 8, 14):
            for wx in range(x + 6, x + bw - 6, 12):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 5, wy + 7],
                                fill=rnd.choice([(255, 214, 120), (255, 120, 160), (120, 220, 255)]))
        x += bw + rnd.randint(4, 12)
    # palm silhouettes
    for px, ph in [(s * 0.12, s * 0.30), (s * 0.85, s * 0.34)]:
        d.line([px, s, px, s - ph], fill=(12, 6, 26), width=6)
        for a in range(-70, 71, 28):
            import math
            r = math.radians(a)
            d.line([px, s - ph, px + math.sin(r) * 42, s - ph - math.cos(r) * 26],
                   fill=(12, 6, 26), width=5)
    return img

def draw_voyager_panel(size):
    """Voyager 1 in interstellar space, drawn with PIL."""
    s = size
    img = Image.new("RGB", (s, s), (4, 6, 18))
    d = ImageDraw.Draw(img)
    import random, math
    rnd = random.Random(11)
    for _ in range(140):
        x, y = rnd.randint(0, s - 1), rnd.randint(0, s - 1)
        r = rnd.random()
        c = (255, 255, 255) if r > 0.85 else (200, 210, 255) if r > 0.6 else (150, 160, 200)
        d.ellipse([x, y, x + (2 if r > 0.9 else 1), y + (2 if r > 0.9 else 1)], fill=c)
    # light beam from Earth (bottom-left) to the probe
    cx, cy = s * 0.68, s * 0.38
    d.line([s * 0.08, s * 0.92, cx - 30, cy + 18], fill=(90, 160, 255), width=3)
    d.ellipse([s * 0.05, s * 0.89, s * 0.11, s * 0.95], fill=(90, 160, 255))
    # dish
    d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], outline=(235, 215, 150), width=5)
    d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(88, 84, 118))
    d.line([cx, cy, cx + 26, cy + 26], fill=(220, 200, 140), width=4)
    # body
    d.rectangle([cx - 14, cy + 20, cx + 44, cy + 52], fill=(200, 200, 210))
    d.rectangle([cx - 14, cy + 20, cx + 44, cy + 30], fill=(240, 200, 60))
    # boom + RTG
    d.line([cx + 44, cy + 36, cx + 92, cy + 36], fill=(180, 180, 190), width=4)
    d.rectangle([cx + 92, cy + 26, cx + 112, cy + 46], fill=(150, 150, 160))
    # antenna mast
    d.line([cx, cy, cx - 40, cy - 44], fill=(180, 180, 190), width=3)
    return img

def square_crop(img, size):
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w - side) // 2, (h - side) // 2,
                    (w + side) // 2, (h + side) // 2))
    return img.resize((size, size), Image.LANCZOS)

STORIES = [
    dict(kicker="SUMMIT IN SHENZHEN", color=(15, 42, 74),
         head="Three leaders, one table",
         body="Trump, Xi and Putin hold the first-ever trilateral summit on the APEC sidelines, with nuclear arms on the agenda.",
         img="media-generation-summit-0-56a0f836-d798-4732-8ef1-dcd05803e336.webp"),
    dict(kicker="GULF TENSIONS", color=(146, 32, 32),
         head="Tankers hit mines off Hormuz",
         body="Iran says three tankers caught fire after striking mines east of the strait; another tanker was hit off Oman.",
         img="media-generation-tanker-0-598e9166-cb6e-450f-b5c7-df5a1792e753.webp"),
    dict(kicker="THE HAGUE", color=(15, 42, 74),
         head="World Court rules today",
         body="The ICJ delivers its judgment on whether Myanmar committed genocide against the Rohingya.",
         img="media-generation-court-0-753ef835-aed4-43f6-90ec-5b6e0f3d638b.webp"),
    dict(kicker="GAMES", color=(128, 32, 128),
         head="GTA VI is out",
         body="Rockstar's blockbuster launches worldwide after 13 years \u2014 and scores 99 on Metacritic.",
         img="gta"),
    dict(kicker="ART", color=(128, 90, 0),
         head="Van Gogh sells for $190.4m",
         body="\u201cChestnut Trees in Blossom\u201d sets an artist record at Sotheby's after a Nazi-era ownership dispute is settled.",
         img="media-generation-chestnut-0-69fea723-7cb4-41b7-bfa5-6b0fda29b427.webp"),
    dict(kicker="SPACE", color=(15, 42, 74),
         head="Voyager 1, one light-day away",
         body="NASA's probe is now so far that its signals take a full day to reach Earth; NASA marks the milestone today.",
         img="voyager"),
]

def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # --- masthead ---
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 124], fill=GOLD)
    d.text((24, 16), "THURSDAY 19 NOVEMBER 2026",
           font=font(FB, 54), fill=WHITE)
    d.text((24, 82), "THE WORLD IN ONE DAY",
           font=font(FB, 24), fill=(212, 175, 70))

    # --- story grid: 2 cols x 3 rows ---
    margin, gap = 14, 12
    top = 124 + 10
    col_w = (W - 2 * margin - gap) // 2
    row_h = (H - top - margin - 2 * gap) // 3
    img_s = 200
    for i, st in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = margin + col * (col_w + gap)
        y0 = top + row * (row_h + gap)
        d.rectangle([x0, y0, x0 + col_w, y0 + row_h], fill=WHITE,
                    outline=(200, 198, 192), width=2)
        # picture panel, vertically centred
        if st["img"] == "gta":
            panel = draw_gta_panel(img_s)
        elif st["img"] == "voyager":
            panel = draw_voyager_panel(img_s)
        else:
            panel = square_crop(Image.open(os.path.join(ASSETS, st["img"])).convert("RGB"), img_s)
        page.paste(panel, (x0 + 14, y0 + (row_h - img_s) // 2))
        # text column
        tx = x0 + 14 + img_s + 16
        tw = x0 + col_w - 14 - tx
        ty = y0 + 16
        d.text((tx, ty), st["kicker"], font=font(FB, 15), fill=st["color"])
        ty += 26
        for line in wrap(d, st["head"], font(FB, 27), tw):
            d.text((tx, ty), line, font=font(FB, 27), fill=INK)
            ty += 33
        ty += 4
        for line in wrap(d, st["body"], font(FR, 18), tw):
            d.text((tx, ty), line, font=font(FR, 18), fill=(60, 60, 60))
            ty += 24

    out = os.path.join(REPO, "entry.png")
    page.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes", page.size)

if __name__ == "__main__":
    main()
