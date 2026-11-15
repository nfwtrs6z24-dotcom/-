"""Koshien-style matchup telop. Renders RGBA frames to stdout (raw rgba) or a still PNG.
usage: telop.py still out.png [t]   |   telop.py frames  (raw rgba to stdout)
"""
import os
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 60000 / 1001
DUR = 8.0          # seconds total
T_IN, T_OUT = 0.9, 0.6
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SERIF = FD + "NotoSerifJP-900.ttf"
SANS = FD + "NotoSansJP-900.ttf"

HEADER = "第1試合"
LEFT_LABEL, LEFT_TEAM = "一塁側", "日吉少年野球クラブ"
RIGHT_LABEL, RIGHT_TEAM = "三塁側", "八幡浜ジュニアベースボールクラブ"

NAVY = (14, 32, 78)
NAVY2 = (6, 16, 44)
GOLD = (214, 176, 84)
RED = (190, 20, 30)
WHITE = (255, 255, 255)

BAND_Y, BAND_H = 760, 210          # main band
PANEL_W = 860
CENTER_W = 1920 - 2 * 40 - 2 * PANEL_W  # gap for 対


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_size(texts, path, max_w, start):
    s = start
    while s > 20:
        f = font(path, s)
        if all(f.getlength(t) <= max_w for t in texts):
            return s
        s -= 2
    return s


TEAM_SIZE = fit_size([LEFT_TEAM, RIGHT_TEAM], SERIF, PANEL_W - 60, 72)


def text_outlined(d, xy, txt, f, fill, stroke, sw, anchor="mm"):
    d.text(xy, txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)


def build_full():
    """Full telop at 100% (static layers)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # drop shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([40, BAND_Y + 10, W - 40, BAND_Y + BAND_H + 10], fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))

    d = ImageDraw.Draw(img)
    x0, x1 = 40, W - 40
    # band with vertical gradient
    for i in range(BAND_H):
        k = i / BAND_H
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(x0, BAND_Y + i), (x1, BAND_Y + i)], fill=c + (235,))
    # gold rules
    d.rectangle([x0, BAND_Y, x1, BAND_Y + 6], fill=GOLD + (255,))
    d.rectangle([x0, BAND_Y + BAND_H - 6, x1, BAND_Y + BAND_H], fill=GOLD + (255,))

    # header tab
    hf = font(SERIF, 40)
    hw = int(hf.getlength(HEADER)) + 80
    hx0 = W // 2 - hw // 2
    d.polygon([(hx0 - 20, BAND_Y), (hx0 + 10, BAND_Y - 64), (hx0 + hw - 10, BAND_Y - 64), (hx0 + hw + 20, BAND_Y)],
              fill=GOLD + (255,))
    d.text((W // 2, BAND_Y - 32), HEADER, font=hf, fill=NAVY2, anchor="mm")

    lf = font(SANS, 34)
    tf = font(SERIF, TEAM_SIZE)
    for side, (label, team) in enumerate([(LEFT_LABEL, LEFT_TEAM), (RIGHT_LABEL, RIGHT_TEAM)]):
        px0 = x0 + 20 if side == 0 else W - 40 - 20 - PANEL_W
        cx = px0 + PANEL_W // 2
        # label pill
        lw = int(lf.getlength(label)) + 44
        ly = BAND_Y + 52
        d.rounded_rectangle([cx - lw // 2, ly - 26, cx + lw // 2, ly + 26], radius=8,
                            fill=WHITE + (255,))
        d.text((cx, ly), label, font=lf, fill=NAVY2, anchor="mm")
        # team name
        text_outlined(d, (cx, BAND_Y + 140), team, tf, WHITE, (0, 0, 0), 3)

    # center 対 badge
    cx, cy, r = W // 2, BAND_Y + BAND_H // 2 + 8, 52
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=GOLD + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED + (255,))
    d.text((cx, cy - 2), "対", font=font(SERIF, 62), fill=WHITE, anchor="mm")
    return img


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


FULL = None


def frame(t):
    global FULL
    if FULL is None:
        FULL = build_full()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < T_IN:  # wipe open from center
        p = ease(t / T_IN)
        half = int((W / 2) * p)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rectangle([W // 2 - half, 0, W // 2 + half, H], fill=255)
        out.paste(FULL, (0, 0), mask)
        # text fades in during second half
        return out
    elif t > DUR - T_OUT:
        a = max(0.0, (DUR - t) / T_OUT)
        img = FULL.copy()
        alpha = img.getchannel("A").point(lambda v: int(v * a))
        img.putalpha(alpha)
        return img
    return FULL


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        t = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
        frame(t).save(sys.argv[2])
    else:
        n = int(round(DUR * FPS))
        out = sys.stdout.buffer
        cache = None
        for i in range(n):
            t = i / FPS
            im = frame(t)
            out.write(im.tobytes())
