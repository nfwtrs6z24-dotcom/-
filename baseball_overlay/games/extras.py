"""Batter telops + defensive-alignment telop for 八幡浜 (Yawatahama)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")
FD = (os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/") + "fonts/"
SERIF = FD + "NotoSerifJP-900.ttf"
SANS = FD + "NotoSansJP-900.ttf"
NAVY = (14, 32, 78); NAVY2 = (6, 16, 44); GOLD = (214, 176, 84); WHITE = (255, 255, 255); RED = (200, 28, 36)
POS = {"投": "ピッチャー", "捕": "キャッチャー", "一": "ファースト", "二": "セカンド", "三": "サード",
       "遊": "ショート", "左": "レフト", "中": "センター", "右": "ライト"}

# (start_sec, order, name, pos_or_None, pa_no, prior_results)
PAS = [
    (110, 1, "濱田り", "投", 1, []), (178, 2, "堀口", "捕", 1, []), (198, 3, "橋本す", "遊", 1, []), (224, 4, "浜本る", "三", 1, []),
    (890, 5, "矢野", "一", 1, []), (972, 6, "橋本ぎ", "二", 1, []), (1092, 7, "森こ", "中", 1, []),
    (1603, 8, "野島", "左", 1, []), (1668, 9, "石堂ひ", "右", 1, []), (1752, 1, "濱田り", None, 2, ["三振"]),
    (2187, 2, "堀口", None, 2, ["二飛"]), (2283, 3, "橋本す", None, 2, ["死球"]), (2308, 4, "浜本る", None, 2, ["三振"]),
    (2790, 5, "矢野", None, 2, ["四球"]), (2874, 6, "橋本ぎ", None, 2, ["投ゴロ"]), (2960, 7, "森こ", None, 2, ["三振"]),
    (3510, 8, "西宮", "左", 1, []), (3566, 9, "山中", "右", 1, []),
    (3789, 1, "濱田り", None, 3, ["三振", "一ゴロ"]), (3850, 2, "堀口", None, 3, ["二飛", "遊ゴロ"]),
    (3938, 3, "橋本す", None, 3, ["死球", "遊直"]),
]
BAT_DUR = 7.0
FULL = {"濱田り": ("濱田", "陸翔"), "堀口": ("堀口", "大翔"), "橋本す": ("橋本", "澄晴"), "浜本る": ("浜本", "琉生"),
        "矢野": ("矢野", "快知"), "橋本ぎ": ("橋本", "銀河"), "森こ": ("森", "昊生"), "野島": ("野島", "里仁"),
        "石堂ひ": ("石堂", "日向汰"), "西宮": ("西宮", "文之介"), "山中": ("山中", "康正"),
        "池田": ("池田", "煌矢")}


# 新チーム公式戦・練習試合3試合の累計 (打数, 安打)
SEASON = {"濱田り": (8, 5), "堀口": (9, 4), "橋本す": (7, 2), "浜本る": (5, 2), "矢野": (7, 6),
          "橋本ぎ": (7, 3), "森こ": (6, 4), "石堂ひ": (4, 0), "西宮": (1, 1), "野島": (0, 0), "山中": (3, 2)}
TODAY = ["三振", "二飛", "死球", "三振", "四球", "投ゴロ", "三振", "三ゴロ", "三振", "一ゴロ", "遊ゴロ", "遊直",
         "三振", "三振", "三振", "三振", "三振", "一ゴロ", "中2", "中2", "投ゴロ"]


def ab_h(res):
    if res in ("四球", "死球") or res.startswith("犠"):
        return 0, 0
    hit = res.endswith("安") or res[-1:] in ("2", "3") or res.endswith("本")
    return 1, int(hit)


def avg_str(ab, h):
    if ab == 0:
        return "---"
    v = h / ab
    return "1.000" if v >= 1 else ("%.3f" % v)[1:]


def disp(n):
    return " ".join(FULL[n]) if n in FULL else n


def shadow(img, box, r=10):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(box, fill=(0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r)))


def batter_png(order, name, pos, pa_no, prior, path, avg=None):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    x0, y0 = None, 862
    of = ImageFont.truetype(SANS, 34)
    pf = ImageFont.truetype(SERIF, 32)
    nf = ImageFont.truetype(SERIF, 66)
    sf = ImageFont.truetype(SANS, 28)
    label = f"{order}番"
    pos_txt = POS.get(pos, pos) if pos else ""
    name = disp(name)
    name_w = nf.getlength(name)
    tab_w = int(of.getlength(label) + (pf.getlength(pos_txt) + 24 if pos_txt else 0) + 40)
    body_w = int(max(name_w + 80, 560, tab_w + 40))
    body_h = 104
    sub = f"第{pa_no}打席" + ("　" + "・".join(prior) if prior else "")
    sub_h = 46
    x0 = 1920 - 60 - body_w
    shadow(img, [x0 + 4, y0 + 8, x0 + body_w + 4, y0 + body_h + sub_h + 8])
    d = ImageDraw.Draw(img)
    # top tab (gold)
    d.rectangle([x0, y0 - 50, x0 + tab_w, y0], fill=GOLD + (255,))
    d.text((x0 + 18, y0 - 25), label, font=of, fill=NAVY2, anchor="lm")
    if pos_txt:
        d.text((x0 + 18 + of.getlength(label) + 16, y0 - 24), pos_txt, font=pf, fill=RED if pos == "代打" else NAVY2, anchor="lm")
    # body (navy gradient)
    for i in range(body_h):
        k = i / body_h
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(x0, y0 + i), (x0 + body_w, y0 + i)], fill=c + (240,))
    d.rectangle([x0, y0, x0 + 6, y0 + body_h], fill=GOLD + (255,))
    d.text((x0 + 36, y0 + body_h // 2 + 2), name, font=nf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
    # sub strip
    d.rectangle([x0, y0 + body_h, x0 + body_w, y0 + body_h + sub_h], fill=(255, 255, 255, 235))
    d.text((x0 + 20, y0 + body_h + sub_h // 2 + 1), sub, font=sf, fill=NAVY2, anchor="lm")
    if avg is not None:
        af = ImageFont.truetype(SANS, 30)
        d.text((x0 + body_w - 20, y0 + body_h + sub_h // 2 + 1), avg, font=af, fill=RED, anchor="rm")
        lw = af.getlength(avg)
        d.text((x0 + body_w - 28 - lw, y0 + body_h + sub_h // 2 + 2), "打率", font=sf, fill=NAVY2, anchor="rm")
    img.save(path)


# defensive alignment (八幡浜, 1回裏)
DEF = {"投": "濱田り", "捕": "堀口", "一": "矢野", "二": "橋本ぎ", "三": "浜本る", "遊": "橋本す",
       "左": "野島", "中": "森こ", "右": "石堂ひ"}  # keys into FULL


def defense_png(path):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    PW, PH = 720, 640
    x0, y0 = 1920 - PW - 50, 1080 - PH - 50
    shadow(img, [x0 + 6, y0 + 10, x0 + PW + 6, y0 + PH + 10], 12)
    d = ImageDraw.Draw(img)
    # panel
    for i in range(PH):
        k = i / PH
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(x0, y0 + i), (x0 + PW, y0 + i)], fill=c + (235,))
    d.rectangle([x0, y0, x0 + PW, y0 + 58], fill=GOLD + (255,))
    hf = ImageFont.truetype(SERIF, 34)
    d.text((x0 + PW // 2, y0 + 29), "八幡浜　守備位置", font=hf, fill=NAVY2, anchor="mm")
    # field drawing
    cx, hy = x0 + PW // 2, y0 + PH - 40          # home plate
    # outfield arc
    R = 500
    d.pieslice([cx - R, hy - R, cx + R, hy + R], 225, 315, fill=(34, 92, 52, 200))
    r2 = 290
    d.pieslice([cx - r2, hy - r2, cx + r2, hy + r2], 225, 315, fill=(150, 112, 70, 210))
    s = 180  # base distance
    home = (cx, hy); first = (cx + s * 0.707, hy - s * 0.707); second = (cx, hy - s * 1.414); third = (cx - s * 0.707, hy - s * 0.707)
    d.line([home, first, second, third, home], fill=(255, 255, 255, 230), width=3)
    for b in (first, second, third):
        d.rectangle([b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6], fill=WHITE)
    d.polygon([(cx - 7, hy - 4), (cx + 7, hy - 4), (cx + 7, hy + 3), (cx, hy + 9), (cx - 7, hy + 3)], fill=WHITE)
    spots = {
        "投": (cx, hy - s * 0.70), "捕": (cx, hy - 14), "一": (first[0] + 58, first[1] - 22),
        "二": (cx + 98, second[1] + 30), "遊": (cx - 98, second[1] + 30), "三": (third[0] - 58, third[1] - 22),
        "左": (cx - 240, hy - 380), "中": (cx, hy - 470), "右": (cx + 240, hy - 380),
    }
    lf = ImageFont.truetype(SANS, 20)
    nf = ImageFont.truetype(SERIF, 28)
    gf = ImageFont.truetype(SERIF, 22)
    for p, (px, py) in spots.items():
        sur, giv = FULL[DEF[p]]
        tw = max(nf.getlength(sur), gf.getlength(giv), 64) + 22
        bx0, by0 = px - tw / 2, py - 40
        d.rounded_rectangle([bx0, by0, bx0 + tw, by0 + 84], radius=6, fill=(6, 16, 44, 235), outline=GOLD + (255,), width=2)
        d.text((px, by0 + 13), p, font=lf, fill=GOLD, anchor="mm")
        d.text((px, by0 + 40), sur, font=nf, fill=WHITE, anchor="mm")
        d.text((px, by0 + 68), giv, font=gf, fill=WHITE, anchor="mm")
    img.save(path)


if __name__ == "__main__":
    os.makedirs(W + "bat", exist_ok=True)
    cum = dict(SEASON)
    for i, (t, o, n, p, k, pr) in enumerate(PAS):
        ab, h = cum[n]
        a = avg_str(ab, h)
        print(i, n, k, a)
        batter_png(o, n, p, k, pr, W + f"bat/b{i:02d}.png", a)
        da, dh = ab_h(TODAY[i])
        cum[n] = (ab + da, h + dh)
    defense_png(W + "defense.png")
    with open(W + "bat/times.txt", "w") as f:
        for i, pa in enumerate(PAS):
            f.write(f"{i:02d} {pa[0]}\n")


def change_png(rows, path):
    """rows: list of (position, out_name_key, in_name_key)"""
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    hf = ImageFont.truetype(SERIF, 36)
    pf = ImageFont.truetype(SANS, 30)
    nf = ImageFont.truetype(SERIF, 38)
    RH = 74
    PW = 820
    PH = 64 + RH * len(rows) + 16
    x0, y0 = 1920 - PW - 60, 1080 - PH - 60
    shadow(img, [x0 + 6, y0 + 10, x0 + PW + 6, y0 + PH + 10], 12)
    d = ImageDraw.Draw(img)
    for i in range(PH):
        k = i / PH
        c = tuple(int(NAVY[j] * (1 - k) + NAVY2[j] * k) for j in range(3))
        d.line([(x0, y0 + i), (x0 + PW, y0 + i)], fill=c + (240,))
    d.rectangle([x0, y0, x0 + PW, y0 + 60], fill=GOLD + (255,))
    d.text((x0 + PW // 2, y0 + 30), "八幡浜　選手交代", font=hf, fill=NAVY2, anchor="mm")
    for r, (pos, a, b) in enumerate(rows):
        cy = y0 + 64 + RH * r + RH // 2 + 4
        d.rounded_rectangle([x0 + 20, cy - 24, x0 + 190, cy + 24], radius=6, fill=WHITE + (240,))
        d.text((x0 + 105, cy), POS[pos], font=pf, fill=NAVY2, anchor="mm")
        d.text((x0 + 215, cy), disp(a), font=nf, fill=(190, 198, 215), anchor="lm")
        aw = nf.getlength(disp(a))
        ax = x0 + 215 + aw + 22
        d.polygon([(ax, cy - 14), (ax, cy + 14), (ax + 24, cy)], fill=GOLD + (255,))
        d.text((ax + 42, cy), disp(b), font=nf, fill=WHITE, anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
        if r < len(rows) - 1:
            d.line([(x0 + 20, cy + RH // 2), (x0 + PW - 20, cy + RH // 2)], fill=GOLD + (90,), width=1)
    img.save(path)


if __name__ == "__main__":
    change_png([("左", "野島", "西宮"), ("右", "石堂ひ", "山中")], W + "change1.png")
    change_png([("中", "森こ", "池田"), ("投", "濱田り", "矢野"), ("一", "矢野", "濱田り")], W + "change2.png")
