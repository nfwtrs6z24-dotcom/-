"""Starting-lineup card (own team only) with optional player photos.
usage: lineup_card.py out.png [photo_dir]
photo_dir/<order>.jpg (e.g. 1.jpg ... 9.jpg, P.jpg) are used if present; otherwise a silhouette placeholder.
"""
import os
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.abspath(__file__)) + "/")
FD = (os.path.dirname(os.path.abspath(__file__)) + "/") + "fonts/"
SERIF = FD + "NotoSerifJP-900.ttf"; SANS = FD + "NotoSansJP-900.ttf"
NAVY = (14, 32, 78); NAVY2 = (6, 16, 44); GOLD = (214, 176, 84); WHITE = (255, 255, 255); RED = (200, 28, 36)
POSC = {"投": (200, 40, 50), "捕": (60, 90, 200), "一": (190, 150, 30), "二": (190, 150, 30), "三": (190, 150, 30),
        "遊": (190, 150, 30), "左": (40, 150, 70), "中": (40, 150, 70), "右": (40, 150, 70)}

TEAM = "八幡浜ジュニアベースボールクラブ"
TITLE = "スターティングメンバー"
LINEUP = [("1", "矢野 快知", "遊"), ("2", "浜本 琉生", "三"), ("3", "濱田 陸翔", "投"), ("4", "堀口 大翔", "捕"),
          ("5", "橋本 銀河", "一"), ("6", "石堂 日向汰", "二"), ("7", "森 昊生", "中"), ("8", "野島 里仁", "左"),
          ("9", "濱田 悠翔", "右")]


def silhouette(sz):
    im = Image.new("RGB", (sz, sz), (40, 60, 110))
    d = ImageDraw.Draw(im)
    d.ellipse([sz * .3, sz * .14, sz * .7, sz * .54], fill=(120, 140, 180))
    d.ellipse([sz * .12, sz * .58, sz * .88, sz * 1.3], fill=(120, 140, 180))
    return im


def photo(path, sz):
    if path and os.path.exists(path):
        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        return ImageOps.fit(im, (sz, sz), centering=(0.5, 0.3))
    return silhouette(sz)


def main(out, pdir=None):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    PW, RH, PH = 760, 82, 0
    rows = LINEUP
    PH = 150 + RH * len(rows) + 20
    x0, y0 = (1920 - PW) // 2, (1080 - PH) // 2
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([x0 + 8, y0 + 12, x0 + PW + 8, y0 + PH + 12], fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(img)
    for i in range(PH):
        k = i / PH
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(x0, y0 + i), (x0 + PW, y0 + i)], fill=c + (240,))
    d.rectangle([x0, y0, x0 + PW, y0 + 6], fill=GOLD + (255,))
    d.rectangle([x0, y0 + PH - 6, x0 + PW, y0 + PH], fill=GOLD + (255,))
    d.text((x0 + PW // 2, y0 + 50), TEAM, font=ImageFont.truetype(SERIF, 40), fill=WHITE, anchor="mm",
           stroke_width=2, stroke_fill=(0, 0, 0))
    d.rectangle([x0 + 150, y0 + 88, x0 + PW - 150, y0 + 132], fill=GOLD + (255,))
    d.text((x0 + PW // 2, y0 + 110), TITLE, font=ImageFont.truetype(SERIF, 30), fill=NAVY2, anchor="mm")
    of = ImageFont.truetype(SANS, 46); nf = ImageFont.truetype(SERIF, 44); pf = ImageFont.truetype(SANS, 30)
    for r, (o, name, pos) in enumerate(rows):
        ry = y0 + 150 + RH * r
        if r % 2 == 0:
            d.rectangle([x0 + 12, ry, x0 + PW - 12, ry + RH - 6], fill=(28, 48, 100, 245))
        ps = RH - 12
        ph = photo(os.path.join(pdir, f"{o}.jpg") if pdir else None, ps)
        img.paste(ph, (x0 + 24, ry + 3))
        d.rectangle([x0 + 24, ry + 3, x0 + 24 + ps, ry + 3 + ps], outline=GOLD + (255,), width=2)
        d.text((x0 + 140, ry + RH // 2 - 3), o, font=of, fill=GOLD, anchor="mm")
        d.text((x0 + 185, ry + RH // 2 - 3), name, font=nf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
        bx = x0 + PW - 90
        d.rounded_rectangle([bx, ry + 12, bx + 60, ry + RH - 18], radius=6, fill=POSC[pos] + (255,))
        d.text((bx + 30, ry + RH // 2 - 3), pos, font=pf, fill=WHITE, anchor="mm")
    img.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
