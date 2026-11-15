"""Metallic / slanted broadcast-game variant (original design): scoreboard + batter telop."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SANS = FD + "NotoSansJP-900.ttf"; SERIF = FD + "NotoSerifJP-900.ttf"
BLK1 = (40, 42, 48); BLK2 = (8, 9, 12); SIL1 = (235, 238, 244); SIL2 = (150, 156, 168)
RED1 = (225, 30, 45); RED2 = (130, 10, 20); WHITE = (255, 255, 255); GOLD = (240, 200, 90)


def vgrad(size, c1, c2, mid=None):
    w, h = size
    g = Image.new("RGBA", size)
    d = ImageDraw.Draw(g)
    for i in range(h):
        k = i / max(1, h - 1)
        if mid is not None:  # metallic: bright band at top third
            k = abs(k - mid) / max(mid, 1 - mid)
        c = tuple(int(c1[j] * (1 - k) + c2[j] * k) for j in range(3))
        d.line([(0, i), (w, i)], fill=c + (255,))
    return g


def paste_poly(img, pts, tex_c1, tex_c2, mid=None):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1
    tex = vgrad((x1 - x0, y1 - y0), tex_c1, tex_c2, mid)
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    img.paste(tex, (x0, y0), m)


def shadow(img, pts, rad=8):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 6, y + 8) for x, y in pts], fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(rad)))


def para(x0, y0, w, h, s):  # slanted parallelogram
    return [(x0 + s, y0), (x0 + w + s, y0), (x0 + w, y0 + h), (x0, y0 + h)]


def scoreboard(inning, half, away, home, out, AWAY="八幡浜", HOME="中田ジャパン"):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    X0, Y0, H = 14, 18, 168
    outer = para(X0, Y0, 560, H, 22)
    shadow(img, outer)
    paste_poly(img, outer, BLK1, BLK2)
    d = ImageDraw.Draw(img)
    d.line(outer + [outer[0]], fill=SIL2 + (255,), width=3)
    # inning block (red metallic)
    ib = para(X0 + 8, Y0 + 8, 132, H - 16, 18)
    paste_poly(img, ib, RED1, RED2, mid=0.25)
    d = ImageDraw.Draw(img)
    cx, cy = X0 + 8 + 66 + 9, Y0 + H // 2
    if half == "final":
        f = ImageFont.truetype(SERIF, 32)
        d.text((cx, cy - 20), "試合", font=f, fill=WHITE, anchor="mm"); d.text((cx, cy + 20), "終了", font=f, fill=WHITE, anchor="mm")
    else:
        d.text((cx - 12, cy + 4), str(inning), font=ImageFont.truetype(SANS, 76), fill=WHITE, anchor="mm", stroke_width=2, stroke_fill=(60, 0, 0))
        up = half == "top"
        ax = cx + 36
        if up:
            d.polygon([(ax, cy - 30), (ax - 14, cy - 10), (ax + 14, cy - 10)], fill=WHITE)
        else:
            d.polygon([(ax, cy + 30), (ax - 14, cy + 10), (ax + 14, cy + 10)], fill=WHITE)
        d.text((ax, cy + (14 if up else -14)), "表" if up else "裏", font=ImageFont.truetype(SERIF, 26), fill=WHITE, anchor="mm")
    nf = ImageFont.truetype(SANS, 42); sf = ImageFont.truetype(SANS, 62)
    for i, (n, s) in enumerate([(AWAY, away), (HOME, home)]):
        ry = Y0 + 10 + i * 76
        row = para(X0 + 150, ry, 300, 70, 10)
        paste_poly(img, row, SIL1, SIL2, mid=0.3)
        d = ImageDraw.Draw(img)
        bat = (half == "top" and i == 0) or (half == "bottom" and i == 1)
        if bat:
            d.polygon([(X0 + 166, ry + 22), (X0 + 166, ry + 50), (X0 + 184, ry + 36)], fill=RED1)
        d.text((X0 + 194, ry + 37), n, font=nf, fill=BLK2, anchor="lm")
        d.text((X0 + 520, ry + 38), str(s), font=sf, fill=GOLD if bat else WHITE, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(out)


def batter(order, pos, name, sub, out, photo=True):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    nf = ImageFont.truetype(SANS, 62); sf = ImageFont.truetype(SANS, 28); tf = ImageFont.truetype(SANS, 32)
    BW = int(max(nf.getlength(name) + 160, 660)); PS = 150
    xr = 1880; y0 = 806; H = 206
    x0 = xr - BW - (PS + 10 if photo else 0)
    outer = para(x0, y0, xr - x0 - 20, H, 20)
    shadow(img, outer)
    paste_poly(img, outer, BLK1, BLK2)
    d = ImageDraw.Draw(img)
    d.line(outer + [outer[0]], fill=SIL2 + (255,), width=3)
    bx = x0 + 14
    if photo:
        pp = para(bx, y0 + 40, PS, PS - 16, 12)
        paste_poly(img, pp, (90, 100, 120), (50, 56, 70))
        d = ImageDraw.Draw(img)
        d.ellipse([bx + PS * .32, y0 + 52, bx + PS * .7, y0 + 52 + PS * .38], fill=(150, 160, 180))
        d.chord([bx + PS * .14, y0 + 40 + PS * .55, bx + PS * .9, y0 + 40 + PS * 1.25], 180, 360, fill=(150, 160, 180))
        d.line(pp + [pp[0]], fill=SIL1 + (255,), width=2)
        bx += PS + 10
    # header: order + position on red slanted tab
    tab = f"{order}番  {pos}"
    tw = int(tf.getlength(tab) + 50)
    paste_poly(img, para(bx, y0 + 8, tw, 40, 12), RED1, RED2, mid=0.3)
    d = ImageDraw.Draw(img)
    d.text((bx + 26, y0 + 28), tab, font=tf, fill=WHITE, anchor="lm")
    # name plate (silver)
    nw = xr - 40 - bx
    paste_poly(img, para(bx, y0 + 54, nw, 92, 14), SIL1, SIL2, mid=0.3)
    d = ImageDraw.Draw(img)
    d.text((bx + 34, y0 + 101), name, font=nf, fill=BLK2, anchor="lm")
    d.text((bx + 10, y0 + 172), sub, font=sf, fill=WHITE, anchor="lm")
    img.save(out)


if __name__ == "__main__":
    o = sys.argv[1]
    scoreboard(5, "bottom", 3, 9, o + "_sb.png")
    batter(3, "ピッチャー", "濱田 陸翔", "第3打席　四球・死球", o + "_bat.png")
