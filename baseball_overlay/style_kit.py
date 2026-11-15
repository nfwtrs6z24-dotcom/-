"""Shared telop kit with two themes: 'pop' (game-pop, rounded, bright) and 'metal' (slanted, black/silver/red).
Provides: matchup, defense, change, lineup.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/", "fonts") + "/"
SANS = FD + "NotoSansJP-900.ttf"; SERIF = FD + "NotoSerifJP-900.ttf"
WHITE = (255, 255, 255); INK = (20, 22, 30)

THEMES = {
    "pop": dict(base=((52, 58, 78), (30, 34, 48)), head=((255, 165, 50), (245, 120, 20)), plate=((70, 180, 245), (20, 110, 200)),
                light=((255, 255, 255), (235, 240, 248)), edge=WHITE, accent=(255, 215, 40), accent2=(230, 50, 60),
                font=SANS, slant=0, radius=16, txt_on_light=INK, field=((70, 170, 80), (40, 130, 60)), dirt=(215, 160, 95)),
    "metal": dict(base=((40, 42, 48), (8, 9, 12)), head=((225, 30, 45), (130, 10, 20)), plate=((235, 238, 244), (150, 156, 168)),
                  light=((235, 238, 244), (150, 156, 168)), edge=(150, 156, 168), accent=(240, 200, 90), accent2=(225, 30, 45),
                  font=SANS, slant=18, radius=0, txt_on_light=(8, 9, 12), field=((40, 90, 55), (20, 55, 30)), dirt=(120, 90, 60)),
}


def _grad(size, c1, c2, mid=None):
    w, h = size
    g = Image.new("RGBA", (max(w, 1), max(h, 1)))
    d = ImageDraw.Draw(g)
    for i in range(h):
        k = i / max(1, h - 1)
        if mid is not None:
            k = abs(k - mid) / max(mid, 1 - mid)
        d.line([(0, i), (w, i)], fill=tuple(int(c1[j] * (1 - k) + c2[j] * k) for j in range(3)) + (255,))
    return g


class Kit:
    def __init__(self, theme):
        self.t = THEMES[theme]; self.name = theme

    def shape(self, box, slant=None):
        x0, y0, x1, y1 = box
        s = self.t["slant"] if slant is None else slant
        return [(x0 + s, y0), (x1, y0), (x1 - s, y1), (x0, y1)]

    def plate(self, img, box, kind="base", outline=True, slant=None, mid=None, shadow=True):
        t = self.t; x0, y0, x1, y1 = [int(v) for v in box]
        c1, c2 = t[kind]
        if mid is None and self.name == "metal" and kind in ("plate", "light", "head"):
            mid = 0.3
        m = Image.new("L", img.size, 0); md = ImageDraw.Draw(m)
        if self.name == "pop":
            md.rounded_rectangle([x0, y0, x1, y1], radius=t["radius"], fill=255)
        else:
            md.polygon(self.shape((x0, y0, x1, y1), slant), fill=255)
        if shadow:
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            sh.paste((0, 0, 0, 160), (0, 0), m.transform(img.size, Image.AFFINE, (1, 0, -6, 0, 1, -8)))
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        tex = Image.new("RGBA", img.size, (0, 0, 0, 0)); tex.paste(_grad((x1 - x0, y1 - y0), c1, c2, mid), (x0, y0))
        img.paste(tex, (0, 0), m)
        if outline:
            d = ImageDraw.Draw(img)
            if self.name == "pop":
                d.rounded_rectangle([x0, y0, x1, y1], radius=t["radius"], outline=t["edge"], width=4)
            else:
                p = self.shape((x0, y0, x1, y1), slant); d.line(p + [p[0]], fill=t["edge"], width=3)

    def text(self, img, xy, s, size, fill=WHITE, anchor="mm", stroke=None, font=None):
        d = ImageDraw.Draw(img)
        f = ImageFont.truetype(font or self.t["font"], size)
        if stroke is None:
            stroke = 3 if (self.name == "pop" and fill == WHITE) else 0
        d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)
        return f.getlength(s)

    # ---------- telops ----------
    def matchup(self, out, header, left_lab, left, right_lab, right):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        self.plate(img, (30, 750, 1890, 985), "base")
        hw = 300
        self.plate(img, (960 - hw // 2, 690, 960 + hw // 2, 752), "head", shadow=False)
        self.text(img, (960, 721), header, 40)
        for cx, lab, nm in [(490, left_lab, left), (1430, right_lab, right)]:
            self.plate(img, (cx - 90, 772, cx + 90, 822), "light", shadow=False, slant=10)
            self.text(img, (cx, 797), lab, 30, fill=self.t["txt_on_light"])
            size = 56
            while ImageFont.truetype(self.t["font"], size).getlength(nm) > 800 and size > 30:
                size -= 2
            self.text(img, (cx, 900), nm, size, stroke=3, fill=WHITE)
        d = ImageDraw.Draw(img)
        if self.name == "pop":
            d.ellipse([905, 815, 1015, 925], fill=self.t["accent2"], outline=WHITE, width=5)
            self.text(img, (960, 868), "VS", 52)
        else:
            self.plate(img, (900, 820, 1020, 916), "head", shadow=False, slant=16)
            self.text(img, (960, 868), "VS", 54)
        img.save(out)

    def defense(self, out, team, DEF):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        PW, PH = 790, 680
        x0, y0 = 1920 - PW - 40, 1080 - PH - 40
        self.plate(img, (x0, y0, x0 + PW, y0 + PH), "base")
        self.plate(img, (x0 + 20, y0 + 14, x0 + PW - 20, y0 + 70), "head", shadow=False, slant=14)
        self.text(img, (x0 + PW // 2, y0 + 42), team + "　守備位置", 34)
        d = ImageDraw.Draw(img)
        cx, hy = x0 + PW // 2, y0 + PH - 40
        R, r2, s = 490, 285, 180
        d.pieslice([cx - R, hy - R, cx + R, hy + R], 225, 315, fill=self.t["field"][0] + (255,))
        d.pieslice([cx - r2, hy - r2, cx + r2, hy + r2], 225, 315, fill=self.t["dirt"] + (255,))
        home = (cx, hy); first = (cx + s * .707, hy - s * .707); second = (cx, hy - s * 1.414); third = (cx - s * .707, hy - s * .707)
        d.line([home, first, second, third, home], fill=WHITE, width=3)
        for b in (first, second, third):
            d.rectangle([b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6], fill=WHITE)
        spots = {"投": (cx, hy - s * .70), "捕": (cx, hy - 14), "一": (first[0] + 60, first[1] - 22), "二": (cx + 100, second[1] + 30),
                 "遊": (cx - 100, second[1] + 30), "三": (third[0] - 60, third[1] - 22), "左": (cx - 245, hy - 380),
                 "中": (cx, hy - 455), "右": (cx + 245, hy - 380)}
        for p, (px, py) in spots.items():
            nm = DEF.get(p, "")
            sur, giv = (nm.split(" ", 1) + [""])[:2] if nm else ("", "")
            w = max(ImageFont.truetype(self.t["font"], 28).getlength(sur), ImageFont.truetype(self.t["font"], 20).getlength(giv), 62) + 26
            self.plate(img, (px - w / 2, py - 40, px + w / 2, py + 44), "light", shadow=False, slant=8)
            self.plate(img, (px - 20, py - 52, px + 20, py - 24), "head", shadow=False, outline=False, slant=4)
            self.text(img, (px, py - 38), p, 20)
            self.text(img, (px, py + 2), sur, 28, fill=self.t["txt_on_light"])
            self.text(img, (px, py + 28), giv, 20, fill=self.t["txt_on_light"])
        img.save(out)

    def change(self, out, team, rows):
        from telolib import POS
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        RH, PW = 76, 860
        PH = 80 + RH * len(rows) + 20
        x0, y0 = 1920 - PW - 40, 1080 - PH - 40
        self.plate(img, (x0, y0, x0 + PW, y0 + PH), "base")
        self.plate(img, (x0 + 20, y0 + 14, x0 + PW - 20, y0 + 70), "head", shadow=False, slant=14)
        self.text(img, (x0 + PW // 2, y0 + 42), team + "　選手交代", 34)
        for i, (pos, a, b) in enumerate(rows):
            cy = y0 + 84 + RH * i + RH // 2
            self.plate(img, (x0 + 24, cy - 26, x0 + 200, cy + 26), "light", shadow=False, slant=10)
            self.text(img, (x0 + 112, cy), POS[pos], 28, fill=self.t["txt_on_light"])
            aw = self.text(img, (x0 + 224, cy), a, 36, fill=(185, 192, 205), anchor="lm", stroke=0)
            ax = x0 + 224 + (aw if a else 0) + 24
            ImageDraw.Draw(img).polygon([(ax, cy - 15), (ax, cy + 15), (ax + 26, cy)], fill=self.t["accent"])
            self.text(img, (ax + 44, cy), b, 40, anchor="lm", stroke=3)
        img.save(out)

    def lineup(self, out, team, rows, photo_dir=None):
        img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        PW, RH = 820, 84
        PH = 160 + RH * len(rows) + 20
        x0, y0 = (1920 - PW) // 2, (1080 - PH) // 2
        self.plate(img, (x0, y0, x0 + PW, y0 + PH), "base")
        self.text(img, (x0 + PW // 2, y0 + 48), team, 40, stroke=3)
        self.plate(img, (x0 + 170, y0 + 86, x0 + PW - 170, y0 + 136), "head", shadow=False, slant=14)
        self.text(img, (x0 + PW // 2, y0 + 111), "スターティングメンバー", 30)
        pcol = {"投": (210, 40, 50), "捕": (50, 90, 210), "左": (40, 150, 70), "中": (40, 150, 70), "右": (40, 150, 70)}
        for r, (o, nm, pos) in enumerate(rows):
            ry = y0 + 156 + RH * r
            ps = RH - 12
            ph = None
            if photo_dir and os.path.exists(os.path.join(photo_dir, f"{o}.jpg")):
                ph = ImageOps.fit(ImageOps.exif_transpose(Image.open(os.path.join(photo_dir, f"{o}.jpg"))).convert("RGB"), (ps, ps), centering=(.5, .3))
            else:
                ph = Image.new("RGB", (ps, ps), (70, 80, 100)); dd = ImageDraw.Draw(ph)
                dd.ellipse([ps * .3, ps * .14, ps * .7, ps * .54], fill=(150, 160, 180)); dd.ellipse([ps * .12, ps * .6, ps * .88, ps * 1.3], fill=(150, 160, 180))
            img.paste(ph, (x0 + 26, ry + 4))
            ImageDraw.Draw(img).rectangle([x0 + 26, ry + 4, x0 + 26 + ps, ry + 4 + ps], outline=self.t["edge"], width=2)
            self.plate(img, (x0 + 116, ry + 8, x0 + PW - 120, ry + RH - 8), "light", shadow=False, slant=12)
            self.text(img, (x0 + 160, ry + RH // 2), o, 44, fill=self.t["accent2"], stroke=0)
            self.text(img, (x0 + 205, ry + RH // 2), nm, 42, fill=self.t["txt_on_light"], anchor="lm", stroke=0)
            bx = x0 + PW - 100
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([bx, ry + 14, bx + 70, ry + RH - 14], radius=8, fill=pcol.get(pos, (200, 160, 30)), outline=WHITE, width=2)
            self.text(img, (bx + 35, ry + RH // 2), pos, 32, stroke=2)
        img.save(out)
