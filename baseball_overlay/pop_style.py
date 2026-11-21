"""Pop / game-style variant: scoreboard + batter telop. Original design with a bright, playful palette."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SANS = FD + "NotoSansJP-900.ttf"
INK = (25, 25, 35); WHITE = (255, 255, 255); SKY = (60, 170, 240); SKY2 = (20, 110, 200)
ORANGE = (255, 140, 30); RED = (230, 50, 60); YEL = (255, 215, 40); PANEL = (30, 34, 48)


def shadow(img, box, r=12, rad=7):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(box, radius=r, fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(rad)))


def grad(d, box, c1, c2, r=0):
    x0, y0, x1, y1 = box
    for i in range(y1 - y0):
        k = i / max(1, y1 - y0 - 1)
        c = tuple(int(c1[j] * (1 - k) + c2[j] * k) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c + (255,))


def scoreboard(inning, half, away, home, out, AWAY="八幡浜", HOME="中田ジャパン"):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    X0, Y0, IW, NW, SW, RH = 20, 20, 150, 300, 100, 82
    W = IW + NW + SW; H = RH * 2
    shadow(img, [X0 + 4, Y0 + 6, X0 + W + 4, Y0 + H + 6], r=18)
    base = Image.new("RGBA", img.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(base)
    grad(bd, [X0, Y0, X0 + W, Y0 + H], (52, 58, 78), PANEL)
    mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).rounded_rectangle([X0, Y0, X0 + W, Y0 + H], radius=18, fill=255)
    img.paste(base, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([X0, Y0, X0 + W, Y0 + H], radius=18, outline=WHITE, width=4)
    # inning: orange arrow-badge
    cx, cy = X0 + IW // 2, Y0 + H // 2
    if half == "final":
        d.rounded_rectangle([cx - 58, cy - 46, cx + 58, cy + 46], radius=14, fill=RED, outline=WHITE, width=3)
        f = ImageFont.truetype(SANS, 30)
        d.text((cx, cy - 16), "試合", font=f, fill=WHITE, anchor="mm"); d.text((cx, cy + 18), "終了", font=f, fill=WHITE, anchor="mm")
    else:
        up = half == "top"
        pts = ([(cx, cy - 64), (cx + 56, cy - 22), (cx + 56, cy + 48), (cx - 56, cy + 48), (cx - 56, cy - 22)] if up else
               [(cx, cy + 64), (cx + 56, cy + 22), (cx + 56, cy - 48), (cx - 56, cy - 48), (cx - 56, cy + 22)])
        d.polygon(pts, fill=ORANGE, outline=WHITE)
        d.line(pts + [pts[0]], fill=WHITE, width=4)
        oy = 8 if up else -8
        d.text((cx - 14, cy + oy), str(inning), font=ImageFont.truetype(SANS, 58), fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=INK)
        d.text((cx + 28, cy + oy + 4), "表" if up else "裏", font=ImageFont.truetype(SANS, 30), fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=INK)
    nf = ImageFont.truetype(SANS, 42); sf = ImageFont.truetype(SANS, 60)
    for i, (n, s) in enumerate([(AWAY, away), (HOME, home)]):
        y = Y0 + RH * i + RH // 2
        bat = (half == "top" and i == 0) or (half == "bottom" and i == 1)
        ny0 = Y0 + RH * i + 12
        d.rounded_rectangle([X0 + IW + 6, ny0, X0 + IW + NW - 6, ny0 + RH - 24], radius=10, fill=WHITE)
        if bat:
            d.ellipse([X0 + IW + 14, y - 10, X0 + IW + 34, y + 10], fill=YEL, outline=INK, width=2)
        fs = 42
        while ImageFont.truetype(SANS, fs).getlength(n) > NW - 62 and fs > 20:
            fs -= 2
        d.text((X0 + IW + 44, y), n, font=ImageFont.truetype(SANS, fs), fill=INK, anchor="lm")
        d.text((X0 + IW + NW + SW // 2 - 4, y + 2), str(s), font=sf, fill=YEL if bat else WHITE, anchor="mm", stroke_width=3, stroke_fill=INK)
    img.save(out)


def batter(order, pos, name, sub, out, photo=True):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    nf = ImageFont.truetype(SANS, 60); sf = ImageFont.truetype(SANS, 28); tf = ImageFont.truetype(SANS, 32)
    BW = int(max(nf.getlength(name) + 140, 640)); BH, SH = 100, 46; PS = BH + SH
    x0 = 1920 - 60 - BW - (PS if photo else 0); y0 = 860
    shadow(img, [x0 + 4, y0 - 44, x0 + BW + (PS if photo else 0) + 4, y0 + BH + SH + 8], r=16)
    d = ImageDraw.Draw(img)
    px = x0
    if photo:
        d.rounded_rectangle([px, y0, px + PS, y0 + PS], radius=16, fill=(90, 120, 170), outline=WHITE, width=4)
        d.ellipse([px + PS * .3, y0 + PS * .16, px + PS * .7, y0 + PS * .56], fill=(170, 190, 220))
        d.chord([px + PS * .12, y0 + PS * .6, px + PS * .88, y0 + PS * 1.3], 180, 360, fill=(170, 190, 220))
        x0 += PS + 6
    # tab: order + position
    tab = f"{order}番"; tw = int(tf.getlength(tab) + tf.getlength(pos) + 70)
    d.rounded_rectangle([x0, y0 - 52, x0 + BW, y0 + 6], radius=12, fill=PANEL, outline=WHITE, width=3)
    d.rounded_rectangle([x0, y0 - 52, x0 + tw, y0 + 6], radius=12, fill=ORANGE, outline=WHITE, width=3)
    d.text((x0 + 18, y0 - 23), tab, font=tf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=INK)
    d.text((x0 + 30 + tf.getlength(tab), y0 - 23), pos, font=tf, fill=YEL, anchor="lm", stroke_width=2, stroke_fill=INK)
    base = Image.new("RGBA", img.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(base)
    grad(bd, [x0, y0, x0 + BW, y0 + BH], SKY, SKY2)
    mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).rounded_rectangle([x0, y0, x0 + BW, y0 + BH], radius=16, fill=255)
    img.paste(base, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x0 + BW, y0 + BH], radius=16, outline=WHITE, width=4)
    d.text((x0 + 34, y0 + BH // 2 + 2), name, font=nf, fill=WHITE, anchor="lm", stroke_width=4, stroke_fill=INK)
    d.rounded_rectangle([x0, y0 + BH + 4, x0 + BW, y0 + BH + SH + 4], radius=12, fill=WHITE, outline=INK, width=2)
    d.text((x0 + 20, y0 + BH + SH // 2 + 4), sub, font=sf, fill=INK, anchor="lm")
    img.save(out)


if __name__ == "__main__":
    o = sys.argv[1]
    scoreboard(5, "bottom", 3, 9, o + "_sb.png")
    batter(3, "ピッチャー", "濱田 陸翔", "第3打席　四球・死球", o + "_bat.png")
