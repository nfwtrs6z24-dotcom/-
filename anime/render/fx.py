"""演出エフェクト: 砂ぼこり・集中線・スピード線・光・きらめき・アイリス・タイトル文字など"""
import math
import random

import cairo

from common import W, H, ORANGE, OUTLINE, clamp, ellipse, hexc, lerp, seg, setc, smooth


def dust(ctx, x, y, age, strength=1.0, color='#f3ecdc', n=7, seed=0, life=0.55):
    """着地の砂ぼこり。age: 着地からの秒数"""
    if not 0 <= age < life:
        return
    u = age / life
    rng = random.Random(seed)
    for i in range(n):
        a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        d = rng.uniform(30, 90) * strength * (1 - (1 - u) ** 2)
        r = rng.uniform(10, 24) * strength * (0.5 + u)
        ellipse(ctx, x + math.cos(a) * d, y + math.sin(a) * d * 0.45 - u * 14, r, r * 0.8)
        setc(ctx, color, 0.75 * (1 - u) ** 1.5)
        ctx.fill()


def impact(ctx, x, y, age, size=60, color='#ffffff', life=0.16):
    """ぶつかった瞬間の放射線"""
    if not 0 <= age < life:
        return
    u = age / life
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, color, 0.9 * (1 - u))
    ctx.set_line_width(size * 0.09)
    for i in range(7):
        a = math.pi + (i + 0.5) * math.pi / 7
        r0, r1 = size * (0.45 + u * 0.6), size * (0.8 + u * 0.9)
        ctx.move_to(x + math.cos(a) * r0, y + math.sin(a) * r0)
        ctx.line_to(x + math.cos(a) * r1, y + math.sin(a) * r1)
        ctx.stroke()


def speed_lines(ctx, t, speed=2600, n=26, alpha=0.32, seed=1, color='#ffffff'):
    """横に流れるスピード線（連続的に流れる。点滅しない）"""
    rng = random.Random(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(n):
        y = rng.uniform(0, H)
        ln = rng.uniform(180, 520)
        v = speed * rng.uniform(0.7, 1.3)
        x = W + 600 - ((rng.uniform(0, W + 1200) + v * t) % (W + 1200))
        setc(ctx, color, alpha * rng.uniform(0.4, 1.0))
        ctx.set_line_width(rng.uniform(2, 6))
        ctx.move_to(x, y)
        ctx.line_to(x + ln, y)
        ctx.stroke()


def focus_lines(ctx, t, cx=W / 2, cy=H / 2, inner=420, alpha=0.5, n=70, seed=2, color='#ffffff'):
    """集中線（ゆっくり回る。コマごとのちらつきは無し）"""
    rng = random.Random(seed)
    rot = t * 0.15
    setc(ctx, color, alpha)
    for i in range(n):
        a = rot + i * 2 * math.pi / n + rng.uniform(-0.03, 0.03)
        w = rng.uniform(0.006, 0.022)
        r0 = inner * rng.uniform(0.9, 1.5)
        ctx.move_to(cx + math.cos(a) * r0, cy + math.sin(a) * r0 * 0.62)
        ctx.line_to(cx + math.cos(a - w) * 2400, cy + math.sin(a - w) * 2400)
        ctx.line_to(cx + math.cos(a + w) * 2400, cy + math.sin(a + w) * 2400)
        ctx.close_path()
    ctx.fill()


def god_rays(ctx, t, x=1750, y=-150, n=7, alpha=0.10, spread=(1.9, 2.75), length=2200, color='#fff3c4', seed=3):
    """斜めに差し込む光の筋"""
    rng = random.Random(seed)
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    r, g, b, _ = hexc(color)
    for i in range(n):
        a = lerp(spread[0], spread[1], (i + rng.uniform(0.1, 0.9)) / n) + math.sin(t * 0.25 + i) * 0.015
        w = rng.uniform(0.02, 0.055)
        k = alpha * (0.6 + 0.4 * math.sin(t * 0.4 + i * 1.7))
        grad = cairo.RadialGradient(x, y, 100, x, y, length)
        grad.add_color_stop_rgba(0, r, g, b, k)
        grad.add_color_stop_rgba(1, r, g, b, 0)
        ctx.set_source(grad)
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(a - w) * length, y + math.sin(a - w) * length)
        ctx.line_to(x + math.cos(a + w) * length, y + math.sin(a + w) * length)
        ctx.close_path()
        ctx.fill()
    ctx.restore()


def star4(ctx, x, y, r, alpha=1.0, color='#ffffff', rot=0.0):
    """十字のきらめき"""
    if alpha <= 0 or r <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    setc(ctx, color, alpha)
    for k in range(4):
        a = k * math.pi / 2
        ctx.move_to(math.cos(a) * r, math.sin(a) * r)
        b = a + math.pi / 4
        ctx.line_to(math.cos(b) * r * 0.16, math.sin(b) * r * 0.16)
    ctx.close_path()
    ctx.fill()
    ctx.restore()


def sparkles(ctx, t, x0, x1, y0, y1, n=40, seed=4, size=14, alpha=0.9, color='#fffbe6', period=2.6):
    """水面などのきらめき（ゆっくり明滅）"""
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        ph, per = rng.uniform(0, 1), period * rng.uniform(0.7, 1.4)
        u = (t / per + ph) % 1.0
        k = math.sin(u * math.pi) ** 3
        f = (y - y0) / max(1, y1 - y0)
        star4(ctx, x, y, size * (0.5 + f) * k, alpha * k, color)


def twinkle(ctx, x, y, age, size=70, life=0.7, color='#ffffff'):
    """キラッ（1回だけ）"""
    if not 0 <= age < life:
        return
    u = age / life
    k = math.sin(u * math.pi)
    star4(ctx, x, y, size * k, 0.95 * k, color, rot=u * 0.8)
    star4(ctx, x + size * 0.55, y - size * 0.45, size * 0.35 * k, 0.9 * k, color, rot=-u)


class Leaves:
    """風に舞う葉っぱ"""

    def __init__(self, seed, n=14, colors=('#4f9445', '#7cb955', '#3f8f3a', '#c9d86a')):
        rng = random.Random(seed)
        self.items = [(rng.uniform(0, 1), rng.uniform(-0.1, 0.9), rng.uniform(120, 260), rng.uniform(20, 60),
                       rng.uniform(0, 6.28), rng.uniform(10, 26), rng.choice(colors), rng.uniform(1.5, 4))
                      for _ in range(n)]

    def draw(self, ctx, t, direction=-1, alpha=0.9, scale=1.0):
        for x0, y0, vx, vy, ph, size, col, spin in self.items:
            span = W + 400
            x = (x0 * span + direction * vx * t) % span - 200
            y = y0 * H + vy * t + math.sin(t * 1.3 + ph) * 40
            ctx.save()
            ctx.translate(x, y % (H + 100) - 50)
            ctx.rotate(ph + t * spin)
            ctx.scale(scale, scale * abs(math.cos(t * spin * 0.7 + ph)) * 0.8 + 0.2)
            ctx.move_to(-size, 0)
            ctx.curve_to(-size * 0.3, -size * 0.55, size * 0.5, -size * 0.45, size, 0)
            ctx.curve_to(size * 0.5, size * 0.45, -size * 0.3, size * 0.55, -size, 0)
            setc(ctx, col, alpha)
            ctx.fill()
            ctx.restore()


def iris_cover(ctx, cx, cy, r, color=ORANGE):
    """(cx,cy) から広がる円で画面をおおう"""
    if r <= 0:
        return
    g = cairo.RadialGradient(cx - r * 0.25, cy - r * 0.3, r * 0.05, cx, cy, r)
    g.add_color_stop_rgb(0, *hexc('#ffc766')[:3])
    g.add_color_stop_rgb(0.6, *hexc(color)[:3])
    g.add_color_stop_rgb(1, *hexc('#f08418')[:3])
    ctx.set_source(g)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.fill()


def iris_hole(ctx, cx, cy, r, color=ORANGE):
    """(cx,cy) の円の外側をおおう（円が広がると画面が現れる）"""
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-10, -10, W + 20, H + 20)
    ctx.new_sub_path()
    ctx.arc(cx, cy, max(r, 0.01), 0, 2 * math.pi)
    setc(ctx, color)
    ctx.fill()
    ctx.restore()


def pop_mark(ctx, x, y, age, text='!', size=90, color='#ff5a3c', life=1.0):
    """頭の上に出る「！」「？」"""
    if not 0 <= age < life:
        return
    k = 1 + 0.35 * math.exp(-age * 9) * math.cos(age * 22)
    a = clamp((life - age) / 0.2)
    ctx.save()
    ctx.translate(x, y - 20 * smooth(age / 0.2))
    kk = max(0.02, k * smooth(age / 0.08))
    ctx.scale(kk, kk)
    ctx.select_font_face('Zen Maru Gothic Black')
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    ctx.move_to(-ext.x_advance / 2, 0)
    ctx.text_path(text)
    setc(ctx, '#ffffff', a)
    ctx.set_line_width(size * 0.2)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke_preserve()
    setc(ctx, color, a)
    ctx.fill()
    ctx.restore()


def blurred(ctx, draw_fn, factor=6, radius=3):
    """draw_fn(ctx2) を低解像度で描いてぼかし、背景として貼る（被写界深度）"""
    from PIL import Image, ImageFilter
    w, h = W // factor, H // factor
    small = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    c2 = cairo.Context(small)
    c2.scale(1 / factor, 1 / factor)
    draw_fn(c2)
    small.flush()
    im = Image.frombuffer('RGBA', (w, h), bytes(small.get_data()), 'raw', 'BGRA', small.get_stride(), 1)
    im = im.filter(ImageFilter.GaussianBlur(radius))
    data = bytearray(im.tobytes('raw', 'BGRA'))
    s2 = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_RGB24, w, h, w * 4)
    ctx.save()
    ctx.scale(factor, factor)
    ctx.set_source_surface(s2, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
    ctx.paint()
    ctx.restore()


class Title:
    """「ころころ、みかん」の文字が1つずつ跳ねて現れる。最後の「。」はみかん。"""
    TEXT = 'ころころ、みかん'
    SIZE = 196

    def __init__(self, cx=W / 2, base=590, t0=1.0, roll=1.9):
        self.base, self.t0 = base, t0
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8)
        c = cairo.Context(surf)
        c.select_font_face('Zen Maru Gothic Black')
        c.set_font_size(self.SIZE)
        adv = [c.text_extents(ch).x_advance * (0.72 if ch == '、' else 0.97) for ch in self.TEXT]
        self.r = 62
        total = sum(adv) + self.r * 2 + 14
        x = cx - total / 2
        self.glyphs = []
        for ch, a in zip(self.TEXT, adv):
            self.glyphs.append((ch, x, a))
            x += a
        self.ox = x + self.r + 10         # みかん（句点）の最終位置
        self.x_start = -self.r - 40
        self.t_roll = t0 + roll
        # 文字は、転がるみかんが通りすぎた瞬間に跳ねて出る
        self.pops = []
        for ch, gx, a in self.glyphs:
            tt = t0
            while self.orange_x(tt) < gx + a * 0.5 and tt < self.t_roll:
                tt += 0.005
            self.pops.append(tt)

    def pop_times(self):
        return self.pops + [self.t_roll]

    def orange_x(self, t):
        u = clamp((t - self.t0) / (self.t_roll - self.t0))
        return lerp(self.x_start, self.ox, 1 - (1 - u) ** 2.0)

    def draw(self, ctx, t, draw_orange):
        ctx.select_font_face('Zen Maru Gothic Black')
        ctx.set_font_size(self.SIZE)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        for pas in (0, 1, 2):
            for i, (ch, x, a) in enumerate(self.glyphs):
                age = t - self.pops[i]
                if age < 0:
                    continue
                k = max(0.02, smooth(age / 0.1) * (1 + 0.45 * math.exp(-age * 7) * math.cos(age * 20)))
                dy = -70 * math.exp(-age * 6) * abs(math.cos(age * 11))
                wob = math.sin(t * 1.6 + i * 0.8) * 5
                ctx.save()
                ctx.translate(x + a / 2, self.base + dy + wob)
                ctx.rotate(math.sin(i * 1.9) * 0.05)
                ctx.scale(k, k)
                ctx.move_to(-a / 2, 0)
                ctx.text_path(ch)
                if pas == 0:      # 影
                    ctx.translate(0, 0)
                    ctx.set_source_rgba(0.16, 0.08, 0.25, 0.45)
                    ctx.set_line_width(40)
                    ctx.stroke()
                elif pas == 1:    # 白フチ
                    ctx.set_source_rgb(1, 1, 1)
                    ctx.set_line_width(24)
                    ctx.stroke()
                else:             # 本体（みかん色のグラデーション）
                    g = cairo.LinearGradient(0, -self.SIZE * 0.85, 0, self.SIZE * 0.1)
                    g.add_color_stop_rgb(0, *hexc('#ffc24a')[:3])
                    g.add_color_stop_rgb(1, *hexc('#f47a12')[:3])
                    ctx.set_source(g)
                    ctx.fill_preserve()
                    ctx.set_source_rgba(1, 1, 1, 0.0)
                    ctx.new_path()
                ctx.restore()
        # 句点のみかん
        ox = self.orange_x(t)
        landed = t - self.t_roll
        sq = 1.0
        hop = 0.0
        if landed > 0:
            hop = 46 * math.exp(-landed * 5) * abs(math.sin(landed * 9))
            sq = 1 - 0.18 * math.exp(-landed * 14)
        rot = (ox - self.ox) / self.r
        draw_orange(ctx, ox, self.base - self.r * 0.55 - hop, self.r, rot, squash=sq)
