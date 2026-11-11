"""「ころころ、みかん。」各カットの絵作り。

各クラスは start(秒, 全体タイムライン上の開始位置) と dur を持ち、
draw(ctx, t) で t 秒目（カット内の時間）の1フレームを描く。
"""
import json
import math
import os
import random

import cairo

import fx
from common import ground_shadow, set_light
from common import (W, H, OUTLINE, ORANGE, Clouds, Tree, boat, bounce_path, cat, clamp, draw_orange,
                    draw_orange_half, draw_person, ellipse, fill_stroke, grade, gull, hexc, house, islands,
                    lerp, limb, mixc, rrect, sample_path, sea, seg, setc, silhouette, sky, smooth,
                    stone_wall, vignette)

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- セリフ（口パク用）

DEFAULT_LINES = [
    dict(who='na', start=1.0, dur=3.2), dict(who='haru', start=7.0, dur=1.8),
    dict(who='haru', start=10.85, dur=0.5), dict(who='haru', start=15.0, dur=1.0),
    dict(who='ryoshi', start=32.0, dur=1.6), dict(who='haru', start=37.6, dur=1.4),
    dict(who='na', start=45.2, dur=3.6),
]
_lines = None


def lines():
    global _lines
    if _lines is None:
        p = os.path.join(HERE, 'voice_timing.json')
        _lines = json.load(open(p))['lines'] if os.path.exists(p) else DEFAULT_LINES
    return _lines


def talk(who, tg):
    for ln in lines():
        if ln['who'] == who and ln['start'] <= tg <= ln['start'] + ln['dur']:
            u = tg - ln['start']
            return 0.2 + 0.8 * abs(math.sin(u * 10.5))
    return 0.0


def blink(t, seed=0):
    """数秒に1回まばたき"""
    p = (t + seed * 1.37) % 3.7
    return 'closed' if p < 0.12 else 'open'


def squash_at(hits, t, amount=0.3, life=0.14):
    """着地直後のつぶれ具合（1=つぶれなし）"""
    for h, v in hits:
        age = t - h
        if 0 <= age < life:
            return 1 - amount * min(1.0, 0.4 + v) * (1 - age / life)
    return 1.0


def shake_at(hits, t, amp=16, life=0.3):
    s_ = 0.0
    for h, v in hits:
        age = t - h
        if 0 <= age < life:
            s_ += amp * v * math.exp(-age * 12) * math.cos(age * 40)
    return s_


def cam(ctx, cx, cy, zoom=1.0):
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def orange_fn(r, rot=0.0, peeled=False):
    return lambda c, x, y: draw_orange(c, x, y, r, rot, peeled=peeled)


def half_fn(r, rot=0.0):
    return lambda c, x, y: draw_orange_half(c, x, y - r * 0.2, r, rot)


def grass_tufts(ctx, seed, x0, x1, y0, y1, n, color='#5d9a3f', size=14):
    rng = random.Random(seed)
    setc(ctx, color)
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        s = size * (0.6 + (y - y0) / max(1, y1 - y0))
        for k in (-1, 0, 1):
            ctx.move_to(x + k * s * 0.3, y)
            ctx.line_to(x + k * s * 0.6, y - s)
            ctx.stroke()


# ================================================================= S01 段々畑の俯瞰


class S01:
    start, dur = 0.0, 5.0
    MORNING = [(0, '#7ec4ec'), (0.55, '#cfeaf8'), (1, '#f6efe0')]

    def __init__(self):
        rng = random.Random(11)
        self.clouds = Clouds(1, 5, 60, 260, 40, 80)
        self.leaves = fx.Leaves(101, n=9)
        self.edge = lambda y: 240 + (y - 110) * 1.42
        # 静止レイヤー（丘・町）を一度だけ描いておく
        sc = 1.2
        self.sc = sc
        self.pad = 300
        self.layer = cairo.ImageSurface(cairo.FORMAT_ARGB32, int((W + 2 * self.pad) * sc), int(H * sc))
        c = cairo.Context(self.layer)
        c.scale(sc, sc)
        c.translate(self.pad, 0)
        # 海と島
        sea(c, 400, H, '#5aa7d6', '#2f7fb6', lines=True, seed=4)
        islands(c, 402, '#7fa9c4', seed=8, x0=900)
        # 町（海岸）
        c.move_to(self.edge(740), 740)
        c.line_to(W + 10, 770)
        c.line_to(W + 10, 850)
        c.line_to(self.edge(870), 870)
        c.close_path()
        setc(c, '#a4b98a')
        c.fill()
        # 防波堤
        rrect(c, 1450, 852, 470, 10, 4)
        fill_stroke(c, '#d9d6cf', 2)
        for i in range(6):
            boat(c, 1280 + i * 105 + rng.uniform(-20, 20), 880 + rng.uniform(0, 40), 0.16 + rng.uniform(0, 0.05),
                 lw=1.5, stripe=rng.choice(['#2f6db5', '#c0392b', '#2f6db5']))
        houses = []
        for row, (yb, hs) in enumerate([(790, 0.8), (815, 0.9), (842, 1.0)]):
            x = self.edge(yb) - 30
            while x < W + 40:
                w = rng.uniform(34, 64) * hs
                houses.append((x, yb + rng.uniform(-6, 6), w, rng.uniform(22, 40) * hs, rng.randint(0, 999)))
                x += w + rng.uniform(4, 18)
        for x, yb, w, h, sd in houses:
            house(c, x, yb, w, h, wall=rng.choice(['#f1ebe0', '#e9e1d2', '#f6f2ea', '#dfe6ea']),
                  roof=rng.choice(['#4b5a70', '#5a6b7f', '#6b5b52', '#3f4c60']), seed=sd, window=False, lw=1.2)
        # 段々畑（奥＝上から手前＝下へ）
        y, h = 120.0, 16.0
        bands = []
        while y < H + 40:
            bands.append((y, h))
            y += h
            h *= 1.11
        for i, (yt, hb) in enumerate(bands):
            yb = yt + hb
            ex0, ex1 = self.edge(yt), self.edge(yb)
            c.save()
            c.move_to(-20, yt)
            c.line_to(ex0, yt)
            c.line_to(ex1, yb)
            c.line_to(-20, yb)
            c.close_path()
            c.clip()
            gtop = yt + hb * 0.32
            c.rectangle(-20, yt, W, hb * 0.34)
            setc(c, '#6fae4c' if i % 2 else '#79b752')
            c.fill()
            stone_wall(c, -20, gtop, ex1 + 40, yb - gtop, seed=i, block=max(5, hb * 0.3))
            c.restore()
            # 木（各段の上に並ぶ）
            sz = hb * 0.95
            x = rng.uniform(-10, sz)
            trees = []
            while x < ex0 - sz * 0.6:
                trees.append(Tree(rng, x, gtop + 2, sz * rng.uniform(0.85, 1.1)))
                x += sz * rng.uniform(1.05, 1.5)
            for tr in trees:
                tr.draw(c, 0, lw=max(0.8, sz * 0.03))
        # 丘の稜線のふち
        c.move_to(self.edge(110), 110)
        c.line_to(self.edge(H + 40), H + 40)
        setc(c, '#4f7f3a')
        c.set_line_width(3)
        c.stroke()
        # モノレール
        setc(c, '#7a7a7a')
        c.set_line_width(3)
        c.move_to(560, H + 20)
        c.curve_to(560, 800, 400, 500, 330, 240)
        c.stroke()
        for k in range(26):
            u = k / 25
            px = (1 - u) ** 3 * 560 + 3 * (1 - u) ** 2 * u * 560 + 3 * (1 - u) * u * u * 400 + u ** 3 * 330
            py = (1 - u) ** 3 * (H + 20) + 3 * (1 - u) ** 2 * u * 800 + 3 * (1 - u) * u * u * 500 + u ** 3 * 240
            c.move_to(px, py)
            c.line_to(px, py + 6 + (1 - u) * 14)
            c.stroke()

    def draw(self, ctx, t):
        set_light(side=1)
        sky(ctx, self.MORNING)
        g = cairo.RadialGradient(1700, 80, 10, 1700, 80, 600)
        g.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.7)
        g.add_color_stop_rgba(1, 1, 0.97, 0.85, 0)
        ctx.set_source(g)
        ctx.paint()
        self.clouds.draw(ctx, t)
        z = lerp(1.0, 1.07, smooth(t / self.dur))
        ctx.save()
        cam(ctx, lerp(960, 1180, smooth(t / self.dur)), lerp(540, 610, smooth(t / self.dur)), z)
        ctx.scale(1 / self.sc, 1 / self.sc)
        ctx.set_source_surface(self.layer, -self.pad * self.sc, 0)
        ctx.get_source().set_filter(cairo.FILTER_GOOD)
        ctx.paint()
        ctx.restore()
        gull(ctx, 1300 + t * 40, 250 - t * 6, 0.9, t, 0.0)
        gull(ctx, 1380 + t * 36, 285 - t * 4, 0.7, t, 1.7)
        fx.sparkles(ctx, t, 1150, 1900, 330, 560, n=26, seed=14, size=9)
        fx.god_rays(ctx, t, x=1800, y=-200, alpha=0.11)
        self.leaves.draw(ctx, t, direction=-1, alpha=0.85)
        grade(ctx, '#ffe2b0', 0.25)
        vignette(ctx)
        f = 1 - seg(t, 0.0, 0.8)
        if f > 0:
            ctx.set_source_rgba(1, 1, 1, f)
            ctx.paint()


# ================================================================= S02 みかんを掲げるハル


class S02:
    start, dur = 5.0, 5.0

    def __init__(self):
        rng = random.Random(22)
        self.clouds = Clouds(2, 4, 60, 220, 50, 90)
        self.leaves = fx.Leaves(102, n=7)
        self.trees_back = [Tree(rng, x, 470, rng.uniform(150, 190)) for x in (40, 230, 420)]
        self.tree_l = Tree(rng, 120, 760, 330)
        self.tree_r = Tree(rng, 1760, 770, 360)
        self.crate_fruits = [(rng.uniform(-60, 60), rng.uniform(-14, 6)) for _ in range(12)]

    def draw(self, ctx, t):
        tg = self.start + t
        set_light(side=1)
        sky(ctx, S01.MORNING, 0, 560)
        self.clouds.draw(ctx, t)
        sea(ctx, 430, 760, '#69b2dc', '#3f8cc4', t, seed=5)
        islands(ctx, 432, '#86aec8', seed=3)
        fx.sparkles(ctx, t, 0, W, 445, 750, n=40, seed=23, size=10)
        # 奥の段（左上の石垣と木）
        ctx.move_to(-10, 470)
        ctx.line_to(640, 470)
        ctx.line_to(700, 760)
        ctx.line_to(-10, 760)
        ctx.close_path()
        ctx.save()
        ctx.clip()
        stone_wall(ctx, -10, 470, 720, 300, seed=5, block=44)
        ctx.restore()
        rrect(ctx, -10, 455, 660, 22, 8)
        fill_stroke(ctx, '#7ab653', 3)
        for tr in self.trees_back:
            tr.draw(ctx, t)
        # 足元の段
        g = cairo.LinearGradient(0, 740, 0, H)
        g.add_color_stop_rgb(0, *hexc('#8cc35f')[:3])
        g.add_color_stop_rgb(1, *hexc('#5e9a3d')[:3])
        ctx.move_to(-10, 760)
        ctx.curve_to(600, 735, 1300, 745, W + 10, 760)
        ctx.line_to(W + 10, H + 10)
        ctx.line_to(-10, H + 10)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()
        grass_tufts(ctx, 3, 0, W, 780, H, 70)
        self.tree_l.draw(ctx, t)
        self.tree_r.draw(ctx, t)
        # コンテナ
        rrect(ctx, 1260, 880, 170, 80, 6)
        fill_stroke(ctx, '#f2c230', 4)
        for i in range(4):
            ctx.rectangle(1275 + i * 40, 900, 26, 14)
            setc(ctx, '#c99a12')
            ctx.fill()
        for cfx, cfy in self.crate_fruits:
            draw_orange(ctx, 1345 + cfx, 878 + cfy, 18, cfx, leaf=False)

        # じいちゃん: 0-2.3 木の実を摘む → 振り返ってうなずく
        turned = t > 2.3
        if not turned:
            pick = (1560 + math.sin(t * 3) * 14, 520 + math.cos(t * 3) * 10)
            draw_person(ctx, 'jii', 1480, 965, s=1.8, facing=1, reach=pick, reach_back=(1540, 640, 0.6),
                        eyes=blink(t, 2))
        else:
            nod = 10 * math.sin((t - 2.6) * 5) * seg(t, 2.6, 2.8) * (1 - seg(t, 3.8, 4.2))
            draw_person(ctx, 'jii', 1480, 965, s=1.8, facing=-1, nod=nod,
                        eyes='happy' if t > 2.6 else 'open', arms=(-6, 8, 4, 30))

        # ハル: みかんを掲げてぴょんぴょん
        up = seg(t, 0.3, 1.0)
        hop = abs(math.sin((t - 1.0) * 6.0)) * 22 * seg(t, 1.0, 1.3) * (1 - seg(t, 4.4, 4.8))
        hx, hy = 860, 960 - hop
        tx = lerp(905, 1110, up)
        ty = lerp(hy - 240, hy - 380, up)
        draw_person(ctx, 'haru', hx, hy, s=2.1, facing=1, reach=(tx, ty), reach_back=(tx - 25, ty + 10),
                    hold=orange_fn(46, 0.4), mouth=talk('haru', tg), eyes=blink(t, 1), lean=-6 * up)
        fx.twinkle(ctx, tx + 30, ty - 60, t - 1.0, size=90)
        fx.god_rays(ctx, t, x=1950, y=-350, alpha=0.06)
        self.leaves.draw(ctx, t, direction=-1, alpha=0.8)
        grade(ctx, '#ffe2b0', 0.22)
        vignette(ctx)


# ================================================================= S03 みかんが滑る


class S03:
    start, dur = 10.0, 4.0
    LEDGE = 880
    SLIP = 0.5
    FACE = 2.3
    SUB = 2

    def __init__(self):
        rng = random.Random(33)
        self.bokeh = [(rng.uniform(0, W), rng.uniform(0, 780), rng.uniform(40, 140),
                       rng.choice(['#4f9445', '#2f6b3a', '#7cc06a', '#ffb347', '#ffd27a'])) for _ in range(40)]
        r = 150
        self.r = r
        self.path, hits = bounce_path(lambda x: self.LEDGE if x < 1700 else 3000, 960, 470, 520, self.dur, r,
                                      g=3000, rest=0.38)
        self.hl = hits
        self.hits = [(self.start + self.SLIP + h, v) for h, v in hits]

    def backdrop(self, ctx, shift=0.0):
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, *hexc('#bfe3f2')[:3])
        g.add_color_stop_rgb(0.35, *hexc('#8fc77a')[:3])
        g.add_color_stop_rgb(1, *hexc('#5c9a44')[:3])
        ctx.set_source(g)
        ctx.paint()
        for x, y, r, c in self.bokeh:
            ellipse(ctx, (x + shift) % (W + 300) - 150, y, r, r)
            setc(ctx, c, 0.28)
            ctx.fill()

    def draw(self, ctx, t):
        set_light(side=1)
        if t >= self.FACE:
            return self.draw_face(ctx, t - self.FACE)
        self.backdrop(ctx)
        # 石垣の天端
        stone_wall(ctx, -10, self.LEDGE, W + 20, H - self.LEDGE + 10, seed=9, block=70)
        ctx.rectangle(-10, self.LEDGE - 6, W + 20, 14)
        setc(ctx, '#d8d0c0')
        ctx.fill()
        # みかん
        tl = t - self.SLIP
        if t < self.SLIP:
            ox, oy, rot = 960, 470 + math.sin(t * 8) * 3, 0.3
        else:
            _, ox, oy, rot = sample_path(self.path, tl)
            rot = 0.3 + rot
        # 手（左右）
        open_ = seg(t, self.SLIP, self.SLIP + 0.35)
        for sg in (-1, 1):
            hx = 960 + sg * (self.r * 0.95 + open_ * 70)
            hy = 500 + open_ * 60
            bx, by = 960 + sg * 560, H + 120
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for wd, col in ((118, OUTLINE), (106, '#ffd8b5')):
                setc(ctx, col)
                ctx.set_line_width(wd)
                ctx.move_to(bx, by)
                ctx.line_to(hx + sg * 40, hy + 40)
                ctx.stroke()
            for wd, col in ((150, OUTLINE), (138, '#ffd23f')):
                setc(ctx, col)
                ctx.set_line_width(wd)
                ctx.move_to(bx, by)
                ctx.line_to(lerp(bx, hx, 0.18), lerp(by, hy, 0.18))
                ctx.stroke()
            ellipse(ctx, hx, hy, 78, 92)
            fill_stroke(ctx, '#ffd8b5', 6)
            ellipse(ctx, hx - sg * 52, hy - 40 - open_ * 10, 26, 40)
            fill_stroke(ctx, '#ffd8b5', 6)
        if tl > 0:
            ground_shadow(ctx, ox, self.LEDGE + 6, self.r * (1.5 - clamp((self.LEDGE - self.r - oy) / 400) * 0.8), alpha=0.35)
            for i, (h, v) in enumerate(self.hl):
                _, px, py, _ = sample_path(self.path, h)
                fx.dust(ctx, px, py + self.r, tl - h, 1.6 + v, seed=i, n=9)
                fx.impact(ctx, px, py + self.r, tl - h, 150 + 80 * v)
        draw_orange(ctx, ox, oy, self.r, rot, squash=squash_at(self.hl, tl, 0.28))
        if t < self.SLIP + 0.1:
            for sg in (-1, 1):
                hx = 960 + sg * (self.r * 0.95 + open_ * 70)
                for k in range(3):
                    ellipse(ctx, hx - sg * 52, 450 + k * 46 + open_ * 60, 34, 20)
                    fill_stroke(ctx, '#ffd8b5', 5)
        fl = seg(t, self.SLIP, self.SLIP + 0.12) * (1 - seg(t, 1.2, 1.7))
        if fl > 0:
            fx.focus_lines(ctx, t, ox, oy, inner=430, alpha=0.42 * fl, seed=31)
        grade(ctx, '#ffe2b0', 0.2)
        vignette(ctx)

    def draw_face(self, ctx, u):
        """ハルのアップ: びっくり → きりっ → 走り出す"""
        self.backdrop(ctx, shift=-u * 60)
        z = 1.14 - 0.14 * smooth(u / 0.22)
        dash = seg(u, 1.2, 1.7)
        calm = seg(u, 0.85, 1.0)
        ctx.save()
        cam(ctx, 960, 540, z)
        jit = math.sin(u * 55) * 7 * (1 - seg(u, 0.0, 0.45))
        if dash < 0.02:
            arms_up = 1 - calm
            draw_person(ctx, 'haru', 960 + jit, 1470, s=5.2, view='front', shadow=False,
                        eyes='wide' if calm < 0.5 else 'open', mouth=0.95 * (1 - calm),
                        reach=(960 + 300, 760, arms_up), reach_back=(960 - 300, 760, arms_up),
                        lean=0, bob=-10 * math.sin(clamp(u / 0.25) * math.pi))
        else:
            x = 900 + dash ** 2 * 1900
            draw_person(ctx, 'haru', x, 1500, s=5.2, view='side', facing=1, shadow=False,
                        phase=x * 0.012, stride=1.6, mouth=0.35, eyes='open')
        ctx.restore()
        fl = (1 - seg(u, 0.75, 1.05))
        if fl > 0:
            fx.focus_lines(ctx, u, 960, 470, inner=560, alpha=0.5 * fl, seed=32)
        fx.pop_mark(ctx, 1420, 300, u - 0.05, '!', size=230, life=0.95)
        if dash > 0:
            fx.speed_lines(ctx, u, speed=3400, alpha=0.4 * dash, seed=33)
        grade(ctx, '#ffe2b0', 0.2)
        vignette(ctx)


# ================================================================= 段差の地形（S04/S05 共通）


class Steps:
    def __init__(self, x0, y0, sw, sh):
        self.x0, self.y0, self.sw, self.sh = x0, y0, sw, sh

    def idx(self, x):
        return math.floor((x - self.x0) / self.sw)

    def top(self, x):
        return self.y0 + self.idx(x) * self.sh

    def smooth_top(self, x, ramp=None):
        """人物の足元用: 段の角で少し跳ねるようになめらかにする"""
        ramp = ramp or self.sw * 0.35
        k = self.idx(x)
        edge = self.x0 + (k + 1) * self.sw
        u = clamp((x - (edge - ramp * 0.3)) / ramp)
        hopv = math.sin(u * math.pi) * self.sh * 0.35
        return self.y0 + (k + smooth(u)) * self.sh - hopv


# ================================================================= S04 段々畑を転がる


class S04:
    start, dur = 14.0, 6.0
    LAG = 0.6
    SUB = 3

    def __init__(self):
        rng = random.Random(44)
        self.st = Steps(-600, 640, 520, 140)
        self.r = 30
        self.path, hits = bounce_path(self.st.top, -150, self.st.top(-150) - 30, 560, self.dur + 1, self.r,
                                      g=2600, rest=0.45, vy0=-200)
        self.hits = [(self.start + h, v) for h, v in hits if h < self.dur]
        self.hl = [(h, v) for h, v in hits if h < self.dur]
        self.fg = fx.Leaves(104, n=9, colors=('#2f6b3a', '#3f8f3a', '#4f9445'))
        self.trees = {}
        for k in range(-3, 12):
            self.trees[k] = [Tree(rng, self.st.x0 + k * self.st.sw + off, 0, rng.uniform(150, 200))
                             for off in (rng.uniform(60, 160), rng.uniform(330, 440))]
        self.clouds = Clouds(4, 5, 40, 200, 40, 80)

    def orange_at(self, t):
        _, x, y, rot = sample_path(self.path, clamp(t, 0, self.dur + 0.9))
        return x, y, rot

    def haru_x(self, t):
        return self.orange_at(t - self.LAG)[0] - 70 if t > self.LAG else -150 - 70 - (self.LAG - t) * 560

    def draw(self, ctx, t):
        tg = self.start + t
        ox, oy, rot = self.orange_at(t)
        camx = (ox + self.haru_x(t)) / 2 + 120
        camy = sum(self.st.top(camx + d) for d in range(-500, 501, 100)) / 11 - 170
        camy += shake_at(self.hl, t)
        set_light(side=1)
        sky(ctx, [(0, '#86c8ee'), (1, '#e9f6ff')], 0, 520)
        self.clouds.draw(ctx, t)
        sea(ctx, 330, H, '#64aedb', '#3b88c0', t, x0=0, x1=W, seed=6)
        islands(ctx, 332, '#86aec8', seed=12, x0=-200 - camx * 0.05)
        fx.sparkles(ctx, t, 0, W, 345, 700, n=30, seed=24, size=9)
        ctx.save()
        cam(ctx, camx, camy)
        k0 = self.st.idx(camx - W)
        for k in range(k0, k0 + 7):
            x = self.st.x0 + k * self.st.sw
            y = self.st.y0 + k * self.st.sh
            for tr in self.trees.get(k, []):
                tr.y = y + 4
                tr.draw(ctx, t)
        for k in range(k0, k0 + 7):
            x = self.st.x0 + k * self.st.sw
            y = self.st.y0 + k * self.st.sh
            stone_wall(ctx, x, y + 16, self.st.sw + 1, 1400, seed=100 + k, block=42)
            rrect(ctx, x - 2, y - 4, self.st.sw + 4, 26, 6)
            fill_stroke(ctx, '#7cb955', 3)
        # ハル
        hx = self.haru_x(t)
        hy = self.st.smooth_top(hx)
        ph = hx * 0.034
        reach = (ox, oy, 0.55 * seg(t, 0.8, 1.4))
        draw_person(ctx, 'haru', hx, hy + 2, s=1.3, facing=1, phase=ph, stride=1.6, reach=reach,
                    mouth=max(talk('haru', tg), 0.25), eyes='open')
        # 足もとの土けむり
        step_ph = (ph / math.pi) % 1.0
        fx.dust(ctx, hx - 20, hy, step_ph * 0.3, 0.45, seed=int(ph / math.pi), n=4, life=0.3)
        gy = self.st.top(ox)
        ground_shadow(ctx, ox, gy + 4, self.r * (1.7 - clamp((gy - self.r - oy) / 260) * 1.0), alpha=0.32)
        for i, (h, v) in enumerate(self.hl):
            _, px, py, _ = sample_path(self.path, h)
            fx.dust(ctx, px, py + self.r, t - h, 0.8 + v, seed=i)
            fx.impact(ctx, px, py + self.r, t - h, 50 + 50 * v)
        draw_orange(ctx, ox, oy, self.r, rot, squash=squash_at(self.hl, t))
        ctx.restore()
        fx.speed_lines(ctx, t, speed=2400, alpha=0.2, seed=41, n=18)
        self.fg.draw(ctx, t * 5, direction=-1, alpha=0.9, scale=2.0)
        grade(ctx, '#ffe2b0', 0.2)
        vignette(ctx)


# ================================================================= S05 路地の石段


class S05:
    start, dur = 20.0, 6.0
    SUB = 2
    CATX = 830
    HSTART = 2.3

    def __init__(self):
        rng = random.Random(55)
        self.st = Steps(-120, 420, 120, 34)
        self.r = 26
        self.path, hits = bounce_path(self.st.top, -60, self.st.top(-60) - 26, 400, self.dur, self.r,
                                      g=2600, rest=0.35)
        self.hits = [(self.start + h, v * 0.7) for h, v in hits]
        self.hl = hits
        self.tcat = next(p[0] for p in self.path if p[1] > self.CATX - 80)
        self.houses = []
        x = -60
        while x < W + 60:
            w = rng.uniform(250, 360)
            base = self.st.top(x + w / 2) - 90
            self.houses.append((x, base, w, rng.uniform(240, 330), rng.randint(0, 999),
                                rng.choice(['#efe6d6', '#e8dfcf', '#f4efe6']), rng.choice(['#4b5a70', '#56657a', '#5c4f49'])))
            x += w + rng.uniform(30, 90)
        self.pots = [(rng.uniform(100, 1800), rng.choice(['#b5523b', '#a0522d', '#6b7b8c'])) for _ in range(5)]
        self.clouds = Clouds(5, 3, 40, 160, 40, 70)

    def draw(self, ctx, t):
        tg = self.start + t
        set_light(side=1)
        sky(ctx, [(0, '#8fcaee'), (1, '#f2f8fc')], 0, 420)
        self.clouds.draw(ctx, t)
        sea(ctx, 250, 420, '#6db3dc', '#4a95c8', t, seed=8)
        islands(ctx, 252, '#8fb3cb', seed=21)
        fx.sparkles(ctx, t, 0, W, 262, 415, n=24, seed=25, size=8)
        for x, base, w, h, sd, wall, roof in self.houses:
            house(ctx, x, base, w, h, wall=wall, roof=roof, seed=sd, lw=3.5)
        # 塀（段ごと）
        for k in range(-1, 18):
            x = self.st.x0 + k * self.st.sw
            y = self.st.y0 + k * self.st.sh
            stone_wall(ctx, x, y - 110, self.st.sw + 1, 112, seed=200 + k, block=36)
            ctx.rectangle(x, y - 118, self.st.sw + 1, 12)
            setc(ctx, '#d9d2c5')
            ctx.fill()
        # 猫
        ct = t - self.tcat
        jump = math.sin(clamp(ct / 0.55) * math.pi) * 70 if ct > 0 else 0
        pose = seg(ct, 0, 0.15) * (1 - 0.4 * seg(ct, 0.6, 1.0)) if ct > 0 else 0
        cy = self.st.top(self.CATX) - 118
        cat(ctx, self.CATX, cy - jump, 1.25, pose=pose, eyes='open' if ct > 0 else 'closed', facing=1 if ct < 0.5 else -1)
        fx.pop_mark(ctx, self.CATX + 70, cy - 150, ct, '!', size=110, life=0.9)
        # 石段
        for k in range(-1, 18):
            x = self.st.x0 + k * self.st.sw
            y = self.st.y0 + k * self.st.sh
            ctx.rectangle(x, y, self.st.sw + 1, H)
            setc(ctx, '#b9b1a3' if k % 2 else '#b2aa9b')
            ctx.fill()
            ctx.rectangle(x, y, self.st.sw + 1, 9)
            setc(ctx, '#d8d1c3')
            ctx.fill()
            setc(ctx, '#7d7466')
            ctx.set_line_width(3)
            ctx.move_to(x, y)
            ctx.line_to(x, y + self.st.sh)
            ctx.stroke()
        for px, col in self.pots:
            y = self.st.top(px)
            ctx.move_to(px - 22, y)
            ctx.line_to(px - 28, y - 40)
            ctx.line_to(px + 28, y - 40)
            ctx.line_to(px + 22, y)
            ctx.close_path()
            fill_stroke(ctx, col, 3)
            for dx in (-16, 0, 16):
                ellipse(ctx, px + dx, y - 56, 20, 18)
                fill_stroke(ctx, '#4f9445', 3)
        # ハル
        if t > self.HSTART:
            hx = -160 + (t - self.HSTART) * 760
            hy = self.st.smooth_top(hx)
            draw_person(ctx, 'haru', hx, hy + 2, s=1.4, facing=1, phase=hx * 0.032, stride=1.6, mouth=0.3)
        _, ox, oy, rot = sample_path(self.path, t)
        gy = self.st.top(ox)
        ground_shadow(ctx, ox, gy + 3, self.r * (1.6 - clamp((gy - self.r - oy) / 200) * 0.9), alpha=0.3)
        for i, (h, v) in enumerate(self.hl):
            _, px, py, _ = sample_path(self.path, h)
            fx.dust(ctx, px, py + self.r, t - h, 0.5 + v, seed=i, n=5)
            fx.impact(ctx, px, py + self.r, t - h, 36 + 40 * v)
        draw_orange(ctx, ox, oy, self.r, rot, squash=squash_at(self.hl, t, 0.25))
        fx.god_rays(ctx, t, x=1900, y=-300, alpha=0.07, n=5)
        grade(ctx, '#ffe2b0', 0.18)
        vignette(ctx)
        # みかん色のワイプで次のカットへ
        wp = seg(t, self.dur - 0.55, self.dur - 0.05)
        if wp > 0:
            fx.iris_cover(ctx, W + 80, 940, wp * 2500)


# ================================================================= 港の背景（S06/S07 共通）


class Harbor:
    def __init__(self, seed=66):
        self.clouds = Clouds(seed, 5, 40, 260, 50, 90)

    def draw(self, ctx, t, horizon=520, quay=800, warm=0.0):
        sky(ctx, [(0, mixc('#8cc0e6', '#e9a46b', warm * 0.5)), (0.7, mixc('#f3dcb8', '#ffc08a', warm)),
                  (1, mixc('#fbe9cf', '#ffd3a0', warm))], 0, horizon)
        self.clouds.draw(ctx, t, color=mixc('#ffffff', '#ffe0c0', warm), alpha=0.85)
        sea(ctx, horizon, quay, mixc('#6ba7cf', '#c79a8a', warm * 0.6), mixc('#2f6f9e', '#4a6f92', warm * 0.5), t,
            line_color='#fff4dc', seed=9)
        islands(ctx, horizon + 1, mixc('#7f9fb8', '#9c8aa0', warm), seed=31)
        boat(ctx, 380, quay - 70, 1.0, t, 0.0)
        boat(ctx, 1500, quay - 95, 0.8, t, 1.3, stripe='#c0392b')
        boat(ctx, 950, quay - 140, 0.55, t, 2.1)
        # 岸壁
        ctx.rectangle(-10, quay, W + 20, H - quay + 10)
        setc(ctx, '#c9c2b5')
        ctx.fill()
        ctx.rectangle(-10, quay - 6, W + 20, 14)
        setc(ctx, '#e3ddd2')
        ctx.fill()
        setc(ctx, '#a69e90')
        ctx.set_line_width(2)
        for i in range(12):
            x = i * 190 + 40
            ctx.move_to(x, quay + 8)
            ctx.line_to(x - 60, H)
            ctx.stroke()


# ================================================================= S06 漁師が拾う


class S06:
    start, dur = 26.0, 5.0
    FLOOR = 985
    STOP = 1.8

    def __init__(self):
        self.bg = Harbor(66)
        self.r = 24

    def orange_x(self, t):
        if t < self.STOP:
            u = t / self.STOP
            return lerp(-60, 1013, 1 - (1 - u) ** 2)
        return 1013 - 14 * math.sin(math.pi * clamp((t - self.STOP) / 0.35))

    def draw(self, ctx, t):
        set_light(side=-1, rim='#ffd9a0', rim_strength=0.3, shadow='#5a3f7a')
        ctx.save()
        cam(ctx, 930, 720, 1.4 + 0.04 * smooth(t / self.dur))
        self.bg.draw(ctx, t, horizon=520, quay=800, warm=0.35)
        fx.sparkles(ctx, t, 200, 1700, 530, 790, n=34, seed=26, size=8)
        gull(ctx, 200 + t * 70, 200, 1.1, t, 0.3)
        gull(ctx, 120 + t * 64, 250, 0.9, t, 1.9)
        # ボラード
        ellipse(ctx, 330, 860, 46, 16)
        fill_stroke(ctx, '#2d2d33', 3)
        rrect(ctx, 300, 790, 60, 70, 10)
        fill_stroke(ctx, '#2d2d33', 3)
        ellipse(ctx, 330, 790, 46, 16)
        fill_stroke(ctx, '#3d3d45', 3)
        # 魚箱と網
        for i, (x, y) in enumerate([(1560, 985), (1700, 985), (1630, 905)]):
            rrect(ctx, x - 60, y - 80, 120, 80, 6)
            fill_stroke(ctx, '#3f7fc4', 4)
        ellipse(ctx, 1330, 975, 120, 34)
        fill_stroke(ctx, '#3f7a52', 4)
        setc(ctx, '#2c5a3c')
        ctx.set_line_width(2)
        for i in range(-5, 6):
            ctx.move_to(1330 + i * 20, 945)
            ctx.line_to(1330 + i * 24, 1005)
            ctx.stroke()
        # 腰かけの箱
        rrect(ctx, 1080, 880, 150, 105, 6)
        fill_stroke(ctx, '#3f7fc4', 4)
        # みかん
        ox = self.orange_x(t)
        oy = self.FLOOR - self.r
        picked = t > 2.9
        # 漁師
        mend = (1105 + math.sin(t * 4) * 12, 860 + math.cos(t * 4) * 6)
        if t < 2.2:
            tgt, w = mend, 1.0
        elif t < 2.9:
            tgt, w = (ox + 6, oy - 4), 1.0
            u = seg(t, 2.2, 2.85)
            tgt = (lerp(mend[0], ox + 6, u), lerp(mend[1], oy - 4, u))
        else:
            u = seg(t, 2.9, 3.7)
            tgt = (lerp(ox + 6, 1060, u), lerp(oy - 4, 720, u))
        happy = t > 3.6
        hands = draw_person(ctx, 'ryoshi', 1155, 880, s=1.6, facing=-1, sit=True, reach=tgt, reach_back=mend,
                            hold=orange_fn(self.r, ox / self.r) if picked else None, lean=8,
                            eyes='happy' if happy else ('open' if t > 1.6 else blink(t)),
                            mouth=0.0, nod=-6 * seg(t, 1.8, 2.1) + 6 * seg(t, 3.0, 3.4))
        self._after(ctx, t, hands, mend, picked, ox, oy)
        fx.pop_mark(ctx, 1215, 600, t - self.STOP - 0.15, '?', size=80, color='#3f7fc4', life=0.9)
        if picked and 'front' in hands:
            fx.twinkle(ctx, hands['front'][0] - 10, hands['front'][1] - 40, t - 3.6, size=60)
        ctx.restore()
        grade(ctx, '#ffcf99', 0.3)
        vignette(ctx)
        if t < 0.7:
            fx.iris_hole(ctx, -80, 940, seg(t, 0.03, 0.65) * 2500)

    def _after(self, ctx, t, hands, mend, picked, ox, oy):
        # 網糸
        setc(ctx, '#3f7a52')
        ctx.set_line_width(2)
        ctx.move_to(*hands.get('back', mend))
        ctx.curve_to(1200, 960, 1260, 960, 1300, 950)
        ctx.stroke()
        if not picked:
            ground_shadow(ctx, ox, self.FLOOR + 2, self.r * 1.6, alpha=0.3)
            fx.dust(ctx, ox + 20, self.FLOOR, t - self.STOP, 0.5, seed=6, n=4)
            fx.impact(ctx, ox + 22, oy, t - self.STOP, 40)
            draw_orange(ctx, ox, oy, self.r, ox / self.r)


# ================================================================= S07 手渡し


class S07:
    start, dur = 31.0, 6.0
    GIVE = 2.4

    def __init__(self):
        self.bg = Harbor(77)

    def draw(self, ctx, t):
        tg = self.start + t
        set_light(side=-1, rim='#ffd08a', rim_strength=0.36, shadow='#5a3f7a')

        def bg(c):
            c.translate(W / 2, H / 2)
            c.scale(1.25, 1.25)
            c.translate(-W / 2, -H / 2 - 60)
            self.bg.draw(c, t, horizon=470, quay=880, warm=0.5)
        fx.blurred(ctx, bg, factor=4, radius=2.0)
        fx.sparkles(ctx, t, 0, W, 545, 880, n=26, seed=27, size=18, alpha=0.75)
        ctx.save()
        cam(ctx, 960, 580, 1.0 + 0.06 * smooth(t / self.dur))
        pant = (1 - seg(t, 0.6, 2.2))
        hbob = math.sin(t * 9) * 7 * pant
        # 漁師
        ext = seg(t, 0.7, 1.7)
        back = seg(t, 2.6, 3.4)
        gx = (lerp(780, 945, ext) if t < self.GIVE else lerp(945, 700, back))
        gy = (lerp(650, 610, ext) if t < self.GIVE else lerp(610, 760, back))
        draw_person(ctx, 'ryoshi', 640, 1060, s=2.2, facing=1, reach=(gx, gy, 1 - back if t > self.GIVE else 1.0),
                    hold=orange_fn(30, 0.6) if t < self.GIVE else None, mouth=talk('ryoshi', tg),
                    eyes='happy' if t > 3.2 else blink(t, 3), lean=4 * ext * (1 - back))
        # ハル
        rch = seg(t, 1.5, 2.2)
        bring = seg(t, 2.5, 3.4)
        if t < self.GIVE:
            tx, ty, w = lerp(1250, 975, rch), lerp(820, 615, rch), max(rch, 0.0)
        else:
            tx, ty, w = lerp(975, 1180, bring), lerp(615, 690, bring), 1.0
        hold = orange_fn(30, 0.6) if t >= self.GIVE else None
        draw_person(ctx, 'haru', 1300, 1060 + hbob, s=2.4, facing=-1, reach=(tx, ty, w),
                    reach_back=(tx + 20, ty + 15, w), hold=hold, lean=12 * pant,
                    mouth=0.45 * pant * abs(math.sin(t * 9)) + (0 if t < 3.3 else 0.0),
                    eyes='happy' if t > 3.4 else 'open')
        fx.twinkle(ctx, 975, 590, t - self.GIVE + 0.1, size=80)
        ctx.restore()
        fx.god_rays(ctx, t, x=-150, y=-200, alpha=0.035, spread=(0.4, 1.25), color='#ffd9a0')
        grade(ctx, '#ffc28a', 0.3)
        vignette(ctx)


# ================================================================= S08 はんぶんこ


class S08:
    start, dur = 37.0, 7.0
    SEAT = 705
    GIVE = 2.5

    def __init__(self):
        rng = random.Random(88)
        self.clouds = Clouds(88, 4, 40, 200, 50, 90)
        self.trees = [Tree(rng, rng.uniform(0, W), rng.uniform(250, 440), rng.uniform(40, 60)) for _ in range(40)]
        self.trees.sort(key=lambda tr: tr.y)
        self.houses = []
        x = -40
        while x < W + 40:
            w = rng.uniform(60, 120)
            self.houses.append((x, 548 + rng.uniform(-8, 4), w, rng.uniform(45, 80), rng.randint(0, 99),
                                rng.choice(['#f1ebe0', '#e9e1d2', '#f6f2ea']), rng.choice(['#4b5a70', '#5a6b7f', '#6b5b52'])))
            x += w + rng.uniform(6, 30)

    def draw(self, ctx, t):
        tg = self.start + t
        set_light(side=-1, rim='#ffcf8a', rim_strength=0.32, shadow='#5a3f7a')
        ctx.save()
        cam(ctx, 960, 600, 1.13 + 0.05 * smooth(t / self.dur))
        sky(ctx, [(0, '#9cc3e4'), (0.6, '#f7d6ae'), (1, '#ffcf9a')], 0, 560)
        self.clouds.draw(ctx, t, color='#fff1e0')
        # 奥の山と段々畑
        ctx.move_to(-10, 560)
        ctx.curve_to(300, 180, 700, 160, 1000, 300)
        ctx.curve_to(1300, 420, 1600, 200, W + 10, 260)
        ctx.line_to(W + 10, 560)
        ctx.close_path()
        setc(ctx, '#7eaa5a')
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        setc(ctx, '#c9bda5')
        ctx.set_line_width(4)
        for i in range(14):
            y = 190 + i * 26
            ctx.move_to(-10, y)
            ctx.curve_to(600, y + 10, 1200, y - 12, W + 10, y + 6)
            ctx.stroke()
        for tr in self.trees:
            tr.draw(ctx, t, lw=1.2)
        ctx.restore()
        for x, y, w, h, sd, wall, roof in self.houses:
            house(ctx, x, y, w, h, wall=wall, roof=roof, seed=sd, window=False, lw=2)
        # 岸壁
        ctx.rectangle(-10, 545, W + 20, self.SEAT - 545)
        setc(ctx, '#cfc8bb')
        ctx.fill()
        ctx.rectangle(-10, self.SEAT, W + 20, 130)
        setc(ctx, '#a8a093')
        ctx.fill()
        setc(ctx, '#8d8578')
        ctx.set_line_width(3)
        for i in range(10):
            ctx.move_to(i * 220 + 60, self.SEAT)
            ctx.line_to(i * 220 + 60, self.SEAT + 130)
            ctx.stroke()
        ctx.rectangle(-10, self.SEAT - 8, W + 20, 12)
        setc(ctx, '#e6e0d5')
        ctx.fill()
        sea(ctx, self.SEAT + 130, H + 120, '#5d86a8', '#35597d', t, line_color='#ffe2bd', line_alpha=0.3, seed=12)
        fx.sparkles(ctx, t, 0, W, self.SEAT + 140, H + 60, n=30, seed=28, size=12, color='#ffe9c4')

        # じいちゃん: 右から歩いてくる → 正面で笑う
        arrive = 2.6
        if t < arrive:
            jx = lerp(2150, 1300, t / arrive)
            draw_person(ctx, 'jii', jx, 640, s=1.7, facing=-1, phase=jx * 0.03, stride=1.0)
        else:
            laugh = seg(t, 4.3, 4.6)
            draw_person(ctx, 'jii', 1300, 640, s=1.7, view='front', eyes='happy' if t > 3.0 else 'open',
                        bob=-abs(math.sin(t * 7)) * 5 * laugh, nod=4 * math.sin(t * 7) * laugh,
                        mouth=0.4 * laugh, arms=(-10, -4, 150, 175) if laugh > 0 else None)

        # 漁師（左に座る）
        haru_cx = 950
        give_pt = (790, 600)
        f_reach = seg(t, 1.9, 2.4)
        if t < self.GIVE:
            ftgt = (lerp(720, give_pt[0], f_reach), lerp(680, give_pt[1], f_reach), f_reach)
        else:
            u = seg(t, 2.9, 3.4)
            down = seg(t, 3.9, 4.4)
            ftgt = (lerp(give_pt[0], 650, u), lerp(give_pt[1], lerp(482, 640, down), u), 1.0)
        laugh = seg(t, 4.4, 4.7)
        eat_f = 0.5 if (3.3 < t < 3.9) else 0.0
        draw_person(ctx, 'ryoshi', 620, self.SEAT, s=1.75, view='front', sit=True,
                    legs=[(0, -4 + math.sin(t * 2) * 5), (0, 6 + math.sin(t * 2 + 1) * 5)],
                    reach=ftgt, hold=half_fn(22) if t >= self.GIVE else None,
                    eyes='happy' if laugh > 0 else blink(t, 4), mouth=max(eat_f, 0.35 * laugh * abs(math.sin(t * 7))),
                    bob=-abs(math.sin(t * 7)) * 4 * laugh)

        # ハル（まん中）
        split = seg(t, 0.6, 1.3)
        offer = seg(t, 1.5, 2.3) * (1 - seg(t, 2.6, 3.1))
        eat = seg(t, 3.4, 3.9) * (1 - seg(t, 4.2, 4.6))
        chest = (haru_cx, 640)
        lx = lerp(chest[0] - 12, chest[0] - 60, split)
        lx, ly = lerp(lx, give_pt[0] + 10, offer), lerp(chest[1], give_pt[1], offer)
        rx = lerp(chest[0] + 12, chest[0] + 60, split)
        rx, ry = lerp(rx, haru_cx + 10, eat), lerp(chest[1], 552, eat)
        raise_ = seg(t, 5.7, 6.3)   # 最後にみかんを夕日にかざす
        rx, ry = lerp(rx, haru_cx + 95, raise_), lerp(ry, 455, raise_)
        if split < 0.05:
            # まるごと（両手で持つ）
            left_hold = orange_fn(34, 0, peeled=True)
            right_hold = None
        else:
            left_hold = half_fn(26, -0.3) if t < self.GIVE else None
            right_hold = half_fn(26, 0.3)
        laugh_h = seg(t, 4.4, 4.7)
        hh = draw_person(ctx, 'haru', haru_cx, self.SEAT, s=1.9, view='front', sit=True,
                    legs=[(0, -6 + math.sin(t * 2.5) * 10), (0, 6 + math.sin(t * 2.5 + 1.5) * 10)],
                    reach=(rx, ry), reach_back=(lx, ly), hold=right_hold, hold_back=left_hold,
                    mouth=max(talk('haru', tg), 0.4 * laugh_h * abs(math.sin(t * 7)), 0.5 if 3.7 < t < 4.2 else 0),
                    eyes='happy' if laugh_h > 0 else blink(t, 5), bob=-abs(math.sin(t * 7)) * 4 * laugh_h)
        # みかんを割ったときの果汁のしぶき
        ja = t - 0.95
        if 0 <= ja < 0.5:
            rng = random.Random(8)
            for _ in range(8):
                a, v = rng.uniform(math.pi * 1.15, math.pi * 1.85), rng.uniform(160, 330)
                px = haru_cx + math.cos(a) * v * ja
                py = 630 + math.sin(a) * v * ja + 500 * ja * ja
                ellipse(ctx, px, py, 5, 7)
                setc(ctx, '#ffb347', 1 - ja / 0.5)
                ctx.fill()
        self.iris = ctx.user_to_device(hh['front'][0], hh['front'][1] - 20)
        ctx.restore()
        grade(ctx, '#ffbf80', 0.33)
        vignette(ctx)
        # かざしたみかんが画面いっぱいに広がる → 次のカットで夕日になる
        wp = (clamp((t - 6.3) / 0.65)) ** 2.2
        if wp > 0:
            fx.iris_cover(ctx, self.iris[0], self.iris[1], 26 + wp * 2500)


# ================================================================= S09 みかん色の夕日


class S09:
    start, dur = 44.0, 8.0
    HZ = 700

    def __init__(self):
        rng = random.Random(99)
        self.leaves = fx.Leaves(109, n=6, colors=('#3a2338', '#5a3a50'))
        self.refl = [(rng.uniform(-1, 1), self.HZ + 8 + i * 9 + rng.uniform(-3, 3), rng.uniform(0, 6.28)) for i in range(36)]

    def draw(self, ctx, t):
        set_light()
        z = lerp(1.12, 1.0, smooth(t / self.dur))
        ctx.save()
        cam(ctx, 960, 620, z)
        sky(ctx, [(0, '#6b4b8f'), (0.45, '#e6735a'), (0.8, '#ffad55'), (1, '#ffd27a')], -200, self.HZ)
        sy = lerp(590, 700, t / self.dur)
        g = cairo.RadialGradient(960, sy, 60, 960, sy, 520)
        g.add_color_stop_rgba(0, 1, 0.92, 0.6, 0.85)
        g.add_color_stop_rgba(1, 1, 0.75, 0.4, 0)
        ctx.set_source(g)
        ctx.rectangle(-W, -H, 3 * W, self.HZ + H)
        ctx.fill()
        ctx.save()
        ctx.rectangle(-W, -H, 3 * W, self.HZ + H)
        ctx.clip()
        ellipse(ctx, 960, sy, 105, 105)
        setc(ctx, '#fff1c2')
        ctx.fill()
        ctx.restore()
        islands(ctx, self.HZ + 1, '#7a4a62', seed=41, x0=-400, x1=W + 400)
        g = cairo.LinearGradient(0, self.HZ, 0, 900)
        g.add_color_stop_rgb(0, *hexc('#e0824f')[:3])
        g.add_color_stop_rgb(1, *hexc('#5a3a66')[:3])
        ctx.set_source(g)
        ctx.rectangle(-W, self.HZ, 3 * W, 400)
        ctx.fill()
        # 夕日の照り返し（ゆっくり揺れる。点滅させない）
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for dx, y, ph in self.refl:
            f = (y - self.HZ) / 330
            w = (120 - f * 40) * (0.7 + 0.3 * math.sin(t * 0.7 + ph))
            setc(ctx, '#ffe7a8', 0.55 - f * 0.25)
            ctx.set_line_width(3 + f * 4)
            x = 960 + dx * 40 * f + math.sin(t * 0.5 + ph) * 10
            ctx.move_to(x - w, y)
            ctx.line_to(x + w, y)
            ctx.stroke()
        fx.sparkles(ctx, t, 640, 1280, self.HZ + 10, 870, n=34, seed=29, size=11, color='#fff0c0', period=3.2)
        sun_dev = ctx.user_to_device(960, sy)
        with silhouette('#3a2338'):
            boat(ctx, 360, self.HZ + 40, 0.6, t, 0.4)
            boat(ctx, 1600, self.HZ + 55, 0.5, t, 2.0)
        gull(ctx, 700 + t * 30, 420, 0.8, t, 0.0)
        gull(ctx, 760 + t * 26, 450, 0.6, t, 1.2)
        # 岸壁と3人のシルエット
        ctx.rectangle(-W, 880, 3 * W, H)
        setc(ctx, '#2a1a2a')
        ctx.fill()
        with silhouette('#2a1a2a'):
            draw_person(ctx, 'jii', 760, 885, s=1.5, view='back', sit=True, arms=(-14, -10, 14, 10))
            draw_person(ctx, 'haru', 960, 885, s=1.6, view='back', sit=True, arms=(-20, -12, 20, 12),
                        bob=-abs(math.sin(t * 1.6)) * 3)
            draw_person(ctx, 'ryoshi', 1170, 885, s=1.5, view='back', sit=True, arms=(-12, -8, 12, 8))
        ctx.restore()
        fx.god_rays(ctx, t, x=sun_dev[0], y=sun_dev[1], n=14, alpha=0.05, spread=(math.pi, 2 * math.pi),
                    length=1500, color='#ffd9a0', seed=9)
        self.leaves.draw(ctx, t, direction=1, alpha=0.5)
        vignette(ctx, 0.3)
        # みかん → 夕日（前のカットのみかん色の円が縮んで太陽になる）
        u = clamp(t / 1.5)
        if u < 1:
            k = (1 - u) ** 3
            r = 105 * z + (2500 - 105 * z) * k
            cx, cy = lerp(sun_dev[0], 1070, k), lerp(sun_dev[1], 400, k)
            col = mixc(ORANGE, '#fff1c2', u ** 2)
            g = cairo.RadialGradient(cx, cy, r * 0.2, cx, cy, r)
            g.add_color_stop_rgb(0, *mixc('#ffc766', '#fff8dc', u ** 2))
            g.add_color_stop_rgb(1, *col)
            ctx.set_source(g)
            ctx.arc(cx, cy, r, 0, 2 * math.pi)
            ctx.fill()


# ================================================================= S10 タイトル背景


class S10:
    start, dur = 52.0, 8.0
    HZ = 780

    def __init__(self):
        self.clouds = Clouds(10, 5, 120, 520, 60, 110)
        self.prev = S09()
        self.title = fx.Title(t0=1.2)

    def chimes(self):
        """効果音用: タイトルの文字が出る時刻（全体タイムライン）"""
        return [self.start + x for x in self.title.pop_times()]

    def draw(self, ctx, t):
        sky(ctx, [(0, '#1f2d5c'), (0.45, '#5d4f8f'), (0.8, '#e88a6a'), (1, '#ffb070')], 0, self.HZ)
        self.clouds.draw(ctx, t * 0.6, color='#f7b6a0', alpha=0.35)
        g = cairo.LinearGradient(0, self.HZ, 0, H)
        g.add_color_stop_rgb(0, *hexc('#c9706a')[:3])
        g.add_color_stop_rgb(1, *hexc('#2a2a52')[:3])
        ctx.set_source(g)
        ctx.rectangle(0, self.HZ, W, H - self.HZ)
        ctx.fill()
        islands(ctx, self.HZ + 1, '#4a3558', seed=51)
        fx.sparkles(ctx, t, 0, W, 20, 430, n=50, seed=30, size=6, alpha=0.85 * seg(t, 0.6, 3.0), period=4.5)
        vignette(ctx, 0.3)
        d = 1 - seg(t, 0.0, 1.3)
        if d > 0:   # 前のカット（夕日）からゆっくり溶けこむ
            ctx.push_group()
            self.prev.draw(ctx, S09.dur + t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(d)
        self.title.draw(ctx, t, draw_orange)
        f = seg(t, 7.5, 8.0)
        if f > 0:
            ctx.set_source_rgba(0, 0, 0, f)
            ctx.paint()


SHOTS = [S01, S02, S03, S04, S05, S06, S07, S08, S09, S10]


def all_hits():
    """効果音用: みかんが跳ねた時刻（全体タイムライン, 強さ）"""
    hits = []
    for cls in (S03, S04, S05):
        hits += cls().hits
    return hits
