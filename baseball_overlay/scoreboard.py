"""Broadcast-style corner scoreboard. render(inning, half, away, home, out_path)
half: 'top' | 'bottom' | 'final'
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SERIF = FD + "NotoSerifJP-900.ttf"
SANS = FD + "NotoSansJP-900.ttf"
NAVY = (14, 32, 78); NAVY2 = (6, 16, 44); GOLD = (214, 176, 84)
RED = (200, 28, 36); WHITE = (255, 255, 255)

AWAY, HOME = "八幡浜", "日吉"       # 先攻 / 後攻
X0, Y0 = 44, 40
NAME_W, SCORE_W, INN_W, ROW_H = 190, 84, 110, 62
W_TOT = NAME_W + SCORE_W + INN_W


def render(inning, half, away, home, path):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    h = ROW_H * 2
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([X0 + 6, Y0 + 8, X0 + W_TOT + 6, Y0 + h + 8], fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(img)
    # name + score panel
    for i in range(h):
        k = i / h
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(X0, Y0 + i), (X0 + NAME_W + SCORE_W, Y0 + i)], fill=c + (240,))
    d.line([(X0, Y0 + ROW_H), (X0 + NAME_W + SCORE_W, Y0 + ROW_H)], fill=GOLD + (200,), width=2)
    d.rectangle([X0, Y0, X0 + 5, Y0 + h], fill=GOLD + (255,))
    nf = ImageFont.truetype(SERIF, 38)
    sf = ImageFont.truetype(SANS, 46)
    batting = 0 if half == "top" else 1 if half == "bottom" else None
    for r, (name, sc) in enumerate([(AWAY, away), (HOME, home)]):
        cy = Y0 + ROW_H * r + ROW_H // 2
        if batting == r:   # at-bat marker
            d.polygon([(X0 + 16, cy - 10), (X0 + 16, cy + 10), (X0 + 30, cy)], fill=GOLD + (255,))
        d.text((X0 + 40, cy), name, font=nf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
        # score cell
        sx0 = X0 + NAME_W
        d.rectangle([sx0, Y0 + ROW_H * r + 6, sx0 + SCORE_W - 8, Y0 + ROW_H * (r + 1) - 6], fill=(255, 255, 255, 235))
        d.text((sx0 + (SCORE_W - 8) // 2, cy + 1), str(sc), font=sf, fill=NAVY2, anchor="mm")
    # inning panel
    ix0 = X0 + NAME_W + SCORE_W
    d.rectangle([ix0, Y0, ix0 + INN_W, Y0 + h], fill=GOLD + (245,))
    cx = ix0 + INN_W // 2
    if half == "final":
        f = ImageFont.truetype(SERIF, 34)
        d.text((cx, Y0 + h // 2 - 22), "試合", font=f, fill=NAVY2, anchor="mm")
        d.text((cx, Y0 + h // 2 + 22), "終了", font=f, fill=NAVY2, anchor="mm")
    else:
        f = ImageFont.truetype(SANS, 54)
        lf = ImageFont.truetype(SERIF, 30)
        d.text((cx - 14, Y0 + h // 2 + 2), str(inning), font=f, fill=NAVY2, anchor="mm")
        d.text((cx + 26, Y0 + h // 2 - (18 if half == "top" else -18)), "表" if half == "top" else "裏",
               font=lf, fill=RED, anchor="mm")
    img.save(path)


if __name__ == "__main__":
    inn, half, a, hm, out = sys.argv[1:6]
    render(int(inn), half, int(a), int(hm), out)
