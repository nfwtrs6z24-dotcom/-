"""Compact game-style scoreboard: inning block on the left, two team rows on the right.
usage: scoreboard2.py inning half away home out.png [AWAY HOME]
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SANS = FD + "NotoSansJP-900.ttf"; SERIF = FD + "NotoSerifJP-900.ttf"
NAVY = (14, 32, 78); NAVY2 = (6, 16, 44); GOLD = (214, 176, 84); WHITE = (255, 255, 255); RED = (220, 40, 50)


def render(inning, half, away, home, out, AWAY="八幡浜", HOME="中田ジャパン"):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    X0, Y0, IW, NW, SW, RH = 20, 20, 150, 300, 100, 82
    W = IW + NW + SW; H = RH * 2
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([X0 + 5, Y0 + 7, X0 + W + 5, Y0 + H + 7], radius=14, fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    d = ImageDraw.Draw(img)
    # outer frame
    d.rounded_rectangle([X0, Y0, X0 + W, Y0 + H], radius=14, fill=NAVY2 + (255,), outline=WHITE + (230,), width=3)
    # inning block (diamond-ish badge)
    cx, cy = X0 + IW // 2, Y0 + H // 2
    r = 62
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD + (255,), outline=WHITE + (255,))
    if half == "final":
        f = ImageFont.truetype(SERIF, 24)
        d.text((cx, cy - 13), "試合", font=f, fill=NAVY2, anchor="mm"); d.text((cx, cy + 15), "終了", font=f, fill=NAVY2, anchor="mm")
    else:
        d.text((cx - 12, cy + 2), str(inning), font=ImageFont.truetype(SANS, 60), fill=NAVY2, anchor="mm")
        d.text((cx + 30, cy + 2), "表" if half == "top" else "裏", font=ImageFont.truetype(SERIF, 30), fill=RED, anchor="mm")
        # arrow above/below the badge
        ay = cy - r - 2 if half == "top" else cy + r + 2
        if half == "top":
            d.polygon([(cx, Y0 + 4), (cx - 11, Y0 + 15), (cx + 11, Y0 + 15)], fill=RED)
        else:
            d.polygon([(cx, Y0 + H - 4), (cx - 11, Y0 + H - 15), (cx + 11, Y0 + H - 15)], fill=RED)
    # divider
    d.line([(X0 + IW, Y0 + 8), (X0 + IW, Y0 + H - 8)], fill=WHITE + (160,), width=2)
    d.line([(X0 + IW + 10, Y0 + RH), (X0 + W - 10, Y0 + RH)], fill=WHITE + (110,), width=2)
    nf = ImageFont.truetype(SERIF, 44); sf = ImageFont.truetype(SANS, 58)
    for i, (n, s) in enumerate([(AWAY, away), (HOME, home)]):
        y = Y0 + RH * i + RH // 2
        bat = (half == "top" and i == 0) or (half == "bottom" and i == 1)
        if bat:
            d.polygon([(X0 + IW + 10, y - 9), (X0 + IW + 10, y + 9), (X0 + IW + 24, y)], fill=GOLD)
        d.text((X0 + IW + 32, y + 1), n, font=nf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
        d.text((X0 + IW + NW + SW // 2 - 4, y + 2), str(s), font=sf, fill=WHITE, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    render(int(a[0]), a[1], int(a[2]), int(a[3]), a[4], *(a[5:7] if len(a) > 5 else []))
