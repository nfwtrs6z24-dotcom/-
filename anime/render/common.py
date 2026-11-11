"""描画の共通部品（色・図形・キャラクター・みかん）。

座標系: 1920x1080、y は下向きが正。
角度の約束: 手足の角度は「真下=0°、前(+x)方向が正、真上=180°」の絶対角度。
"""
import math
import os
import random
import tempfile

_FONT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts'))
_conf = os.path.join(tempfile.gettempdir(), 'korokoro_fonts.conf')
with open(_conf, 'w') as _f:
    _f.write('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
             '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
             f'<dir>{_FONT_DIR}</dir></fontconfig>')
os.environ['FONTCONFIG_FILE'] = _conf

import cairo  # noqa: E402

W, H = 1920, 1080
FPS = 30000 / 1001
OUTLINE = '#3b2a25'

# ---------------------------------------------------------------- 色・数値


def hexc(h, a=1.0):
    if not isinstance(h, str):
        return (h[0], h[1], h[2], a)
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


_SIL = None  # シルエット描画時の上書き色


def setc(ctx, c, a=1.0):
    if _SIL is not None:
        c = _SIL
    if isinstance(c, str):
        r, g, b, _ = hexc(c)
    else:
        r, g, b = c[:3]
    ctx.set_source_rgba(r, g, b, a)


def mixc(c1, c2, t):
    a, b = hexc(c1), hexc(c2)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(t, t0, t1):
    """t0→t1 で 0→1 になるなめらかな補間係数"""
    return smooth((t - t0) / (t1 - t0))


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- 図形


def ellipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill_stroke(ctx, color, lw=4.0, outline=OUTLINE, alpha=1.0):
    setc(ctx, color, alpha)
    if lw > 0:
        ctx.fill_preserve()
        setc(ctx, outline, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    else:
        ctx.fill()


def dirv(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def limb(ctx, x, y, ang, length, width, color, lw=4.0):
    """縁取り付きのカプセル形の手足。終点を返す。"""
    dx, dy = dirv(ang)
    x2, y2 = x + dx * length, y + dy * length
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if lw > 0:
        setc(ctx, OUTLINE)
        ctx.set_line_width(width + lw * 2)
        ctx.move_to(x, y)
        ctx.line_to(x2, y2)
        ctx.stroke()
    setc(ctx, color)
    ctx.set_line_width(width)
    ctx.move_to(x, y)
    ctx.line_to(x2, y2)
    ctx.stroke()
    return x2, y2


def ik2(sx, sy, tx, ty, l1, l2, bend=1):
    """2関節IK。肩(sx,sy)から目標(tx,ty)へ届く上腕・前腕の絶対角度を返す。"""
    dx, dy = tx - sx, ty - sy
    d = clamp(math.hypot(dx, dy), 1e-3, l1 + l2 - 1e-3)
    base = math.degrees(math.atan2(dx, dy))
    c = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    a1 = base + bend * math.degrees(math.acos(c))
    ex, ey = sx + dirv(a1)[0] * l1, sy + dirv(a1)[1] * l1
    a2 = math.degrees(math.atan2(tx - ex, ty - ey))
    return a1, a2


def vignette(ctx, strength=0.22):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.08, 0.04, 0.02, strength)
    ctx.set_source(g)
    ctx.paint()


def grade(ctx, color, alpha, op=cairo.OPERATOR_SOFT_LIGHT):
    ctx.save()
    ctx.set_operator(op)
    r, g, b, _ = hexc(color)
    ctx.set_source_rgba(r, g, b, alpha)
    ctx.paint()
    ctx.restore()


# ---------------------------------------------------------------- みかん

ORANGE = '#ff9a1f'


def draw_orange(ctx, x, y, r, rot=0.0, leaf=True, peeled=False, squash=1.0):
    ctx.save()
    ctx.translate(x, y)
    if squash != 1.0:
        ctx.translate(0, r * (1 - squash))
        ctx.scale(1 / squash ** 0.5, squash)
    if _SIL is None:
        g = cairo.RadialGradient(-r * 0.35, -r * 0.4, r * 0.1, 0, 0, r * 1.05)
        g.add_color_stop_rgb(0, *hexc('#ffc766')[:3])
        g.add_color_stop_rgb(0.55, *hexc(ORANGE)[:3])
        g.add_color_stop_rgb(1, *hexc('#e8720c')[:3])
        ellipse(ctx, 0, 0, r, r * 0.92)
        ctx.set_source(g)
        ctx.fill_preserve()
    else:
        ellipse(ctx, 0, 0, r, r * 0.92)
        setc(ctx, ORANGE)
        ctx.fill_preserve()
    setc(ctx, OUTLINE)
    ctx.set_line_width(max(2.0, r * 0.06))
    ctx.stroke()
    if peeled:
        # 房の筋
        setc(ctx, '#f2b25c')
        ctx.set_line_width(max(1.5, r * 0.04))
        for i in range(-2, 3):
            ctx.move_to(i * r * 0.32, -r * 0.85 + abs(i) * r * 0.12)
            ctx.curve_to(i * r * 0.42, -r * 0.2, i * r * 0.42, r * 0.2, i * r * 0.32, r * 0.85 - abs(i) * r * 0.12)
            ctx.stroke()
    else:
        # 表面のつぶつぶ（回転に合わせて動く）
        ctx.save()
        ctx.rotate(rot)
        setc(ctx, '#e07a10', 0.55)
        rng = random.Random(7)
        for _ in range(14):
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(0.15, 0.8) * r
            ellipse(ctx, math.cos(a) * d, math.sin(a) * d * 0.92, r * 0.035, r * 0.035)
            ctx.fill()
        ctx.restore()
        if leaf:
            sx, sy = math.sin(rot) * r * 0.8, -math.cos(rot) * r * 0.75
            ctx.save()
            ctx.translate(sx, sy)
            ctx.rotate(rot)
            # 葉
            ctx.move_to(0, 0)
            ctx.curve_to(r * 0.25, -r * 0.45, r * 0.75, -r * 0.45, r * 0.9, -r * 0.2)
            ctx.curve_to(r * 0.6, -r * 0.02, r * 0.25, r * 0.02, 0, 0)
            fill_stroke(ctx, '#3f8f3a', max(1.5, r * 0.05))
            ellipse(ctx, 0, 0, r * 0.11, r * 0.09)
            fill_stroke(ctx, '#5a6b2a', max(1.0, r * 0.04))
            ctx.restore()
    # ハイライト
    ellipse(ctx, -r * 0.38, -r * 0.42, r * 0.18, r * 0.1)
    ctx.set_source_rgba(1, 1, 1, 0.55 if _SIL is None else 0)
    ctx.fill()
    ctx.restore()


def draw_orange_half(ctx, x, y, r, rot=0.0):
    """むいた半分のみかん（房が見える断面）"""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(-r, 0)
    ctx.arc(0, 0, r, math.pi, 2 * math.pi)
    ctx.close_path()
    fill_stroke(ctx, '#ffad3b', max(2.0, r * 0.07))
    setc(ctx, '#f7d08a')
    ctx.set_line_width(max(1.5, r * 0.05))
    for i in range(1, 4):
        a = math.pi + i * math.pi / 4
        ctx.move_to(0, 0)
        ctx.line_to(math.cos(a) * r * 0.9, math.sin(a) * r * 0.9)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- キャラクター

SKIN = '#ffd8b5'
SPECS = {
    'haru': dict(leg=74, torso=66, head=40, uarm=32, larm=30, lw=16, tw=52,
                 shirt='#ffd23f', pants='#3d6fb0', shoe='#ffffff', hair='#2a2230'),
    'jii': dict(leg=100, torso=96, head=36, uarm=46, larm=42, lw=19, tw=62,
                shirt='#2e4470', pants='#2e4470', shoe='#5a4a3c', hair='#f2f0ea'),
    'ryoshi': dict(leg=94, torso=100, head=38, uarm=46, larm=42, lw=23, tw=84,
                   shirt='#fbfbf7', pants='#f07a1e', shoe='#1e1e24', hair='#2b2b2b'),
}


def _eyes(ctx, ex, ey, r, eyes, big=False):
    if eyes == 'closed':
        setc(ctx, OUTLINE)
        ctx.set_line_width(r * 0.07)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(ex - r * 0.11, ey)
        ctx.line_to(ex + r * 0.11, ey)
        ctx.stroke()
    elif eyes == 'happy':
        setc(ctx, OUTLINE)
        ctx.set_line_width(r * 0.07)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(ex, ey + r * 0.05, r * (0.13 if big else 0.1), math.pi * 1.1, math.pi * 1.9)
        ctx.stroke()
    elif eyes == 'wide':
        ellipse(ctx, ex, ey, r * 0.17, r * 0.19)
        fill_stroke(ctx, '#ffffff', r * 0.05)
        ellipse(ctx, ex, ey, r * 0.06, r * 0.07)
        setc(ctx, '#231a1e')
        ctx.fill()
    elif big:
        rx, ry = r * 0.115, r * 0.165
        ellipse(ctx, ex, ey, rx, ry)
        setc(ctx, '#2e1c16')
        ctx.fill()
        ctx.save()
        ellipse(ctx, ex, ey, rx, ry)
        ctx.clip()
        ellipse(ctx, ex, ey + ry * 0.75, rx * 1.2, ry * 0.8)
        setc(ctx, '#a05a2c')
        ctx.fill()
        ctx.restore()
        a = 0 if _SIL else 0.97
        ellipse(ctx, ex + rx * 0.3, ey - ry * 0.42, rx * 0.42, ry * 0.3)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.fill()
        ellipse(ctx, ex - rx * 0.35, ey + ry * 0.4, rx * 0.2, ry * 0.14)
        ctx.set_source_rgba(1, 1, 1, a * 0.8)
        ctx.fill()
        setc(ctx, OUTLINE)
        ctx.set_line_width(r * 0.05)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(ex, ey, ry * 1.02, math.pi * 1.2, math.pi * 1.8)
        ctx.stroke()
    else:
        ellipse(ctx, ex, ey, r * 0.075, r * 0.11)
        setc(ctx, '#231a1e')
        ctx.fill()
        ellipse(ctx, ex + r * 0.025, ey - r * 0.04, r * 0.028, r * 0.035)
        ctx.set_source_rgba(1, 1, 1, 0 if _SIL else 0.95)
        ctx.fill()


def _mouth(ctx, mx, my, r, mouth):
    setc(ctx, OUTLINE)
    ctx.set_line_width(r * 0.06)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mouth > 0.05:
        ellipse(ctx, mx, my, r * 0.11, r * 0.05 + r * 0.1 * mouth)
        fill_stroke(ctx, '#b8434a', r * 0.05)
    else:
        ctx.arc(mx, my - r * 0.06, r * 0.12, math.pi * 0.2, math.pi * 0.8)
        ctx.stroke()


def _head(ctx, kind, sp, view, r, mouth, eyes, blush=True):
    hair = sp['hair']
    lw = max(3.0, r * 0.09)
    # 後ろ髪
    if kind == 'haru':
        if view == 'side':
            rrect(ctx, -r * 1.12, -r * 1.12, r * 1.75, r * 1.95, r * 0.75)
        else:
            rrect(ctx, -r * 1.14, -r * 1.12, r * 2.28, r * 1.95, r * 0.8)
        fill_stroke(ctx, hair, lw)
    # 耳（横向き）
    if view == 'side':
        ellipse(ctx, -r * 0.12, r * 0.05, r * 0.17, r * 0.22)
        fill_stroke(ctx, SKIN, lw * 0.8)
    # 顔
    ellipse(ctx, 0, 0, r, r)
    fill_stroke(ctx, SKIN if view != 'back' or kind == 'jii' else hair, lw)
    if view == 'back':
        if kind == 'haru':
            ellipse(ctx, 0, 0, r, r)
            fill_stroke(ctx, hair, lw)
        elif kind == 'ryoshi':
            ctx.arc(0, 0, r, math.pi * 0.95, math.pi * 2.05)
            ctx.close_path()
            fill_stroke(ctx, hair, lw)
    # 髪（前・上）
    if kind == 'haru' and view != 'back':
        ctx.arc(0, 0, r * 1.05, math.radians(198), math.radians(342))
        ctx.close_path()
        fill_stroke(ctx, hair, lw)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        setc(ctx, '#75668f')
        ctx.set_line_width(r * 0.09)
        ctx.arc(0, 0, r * 0.8, math.radians(232), math.radians(272))
        ctx.stroke()
        # 髪どめ
        hx = r * 0.45 if view == 'side' else r * 0.55
        ellipse(ctx, hx, -r * 0.62, r * 0.13, r * 0.13)
        fill_stroke(ctx, ORANGE, lw * 0.7)
    if kind == 'ryoshi' and view != 'back':
        ctx.arc(0, 0, r * 1.02, math.radians(195), math.radians(345))
        ctx.close_path()
        fill_stroke(ctx, hair, lw)
    if kind == 'jii' and view == 'back':
        ellipse(ctx, 0, 0, r, r)
        fill_stroke(ctx, hair, lw)
    if kind == 'jii' and view == 'side':
        ctx.arc(0, -r * 0.05, r, math.radians(135), math.radians(215))
        ctx.close_path()
        fill_stroke(ctx, hair, lw * 0.8)
    if kind == 'jii' and view == 'front':
        for sgn in (-1, 1):
            ellipse(ctx, sgn * r * 0.92, -r * 0.05, r * 0.16, r * 0.3)
            fill_stroke(ctx, hair, lw * 0.7)
    # 顔パーツ
    if view == 'side':
        _eyes(ctx, r * 0.5, -r * 0.08, r, eyes, kind == 'haru')
        if kind != 'haru':
            setc(ctx, OUTLINE)
            ctx.set_line_width(r * 0.06)
            ctx.move_to(r * 0.33, -r * 0.3)
            ctx.line_to(r * 0.66, -r * 0.33)
            ctx.stroke()
        if blush:
            ellipse(ctx, r * 0.42, r * 0.28, r * 0.15, r * 0.08)
            setc(ctx, '#ff8c8c', 0.55)
            ctx.fill()
        _mouth(ctx, r * 0.74, r * 0.45, r, mouth)
    elif view == 'front':
        for sgn in (-1, 1):
            _eyes(ctx, sgn * r * 0.36, -r * 0.05, r, eyes, kind == 'haru')
            if blush:
                ellipse(ctx, sgn * r * 0.55, r * 0.28, r * 0.15, r * 0.08)
                setc(ctx, '#ff8c8c', 0.55)
                ctx.fill()
            if kind != 'haru':
                setc(ctx, OUTLINE)
                ctx.set_line_width(r * 0.06)
                ctx.move_to(sgn * r * 0.22, -r * 0.3)
                ctx.line_to(sgn * r * 0.5, -r * 0.33)
                ctx.stroke()
        _mouth(ctx, 0, r * 0.45, r, mouth)
    # かぶりもの
    if kind == 'jii':
        ctx.save()
        ctx.translate(0, -r * 0.5)
        ellipse(ctx, 0, 0, r * 1.7, r * 0.38)
        fill_stroke(ctx, '#e9c46a', lw)
        ctx.move_to(-r * 0.9, 0)
        ctx.curve_to(-r * 0.9, -r * 1.05, r * 0.9, -r * 1.05, r * 0.9, 0)
        ctx.close_path()
        fill_stroke(ctx, '#f0cf78', lw)
        ctx.rectangle(-r * 0.88, -r * 0.32, r * 1.76, r * 0.2)
        setc(ctx, '#8b3a2e')
        ctx.fill()
        ctx.restore()
    if kind == 'ryoshi':
        y = -r * 0.48
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        setc(ctx, OUTLINE)
        ctx.set_line_width(r * 0.32)
        ctx.move_to(-r * 0.95, y)
        ctx.line_to(r * 0.95, y)
        ctx.stroke()
        setc(ctx, '#ffffff')
        ctx.set_line_width(r * 0.22)
        ctx.move_to(-r * 0.95, y)
        ctx.line_to(r * 0.95, y)
        ctx.stroke()
        setc(ctx, '#2c4a8a')
        ctx.set_line_width(r * 0.06)
        for i in range(-4, 5):
            ctx.move_to(i * r * 0.2 - r * 0.06, y - r * 0.1)
            ctx.line_to(i * r * 0.2 + r * 0.06, y + r * 0.1)
            ctx.stroke()
        if view != 'front':
            kx = -r * 0.95 if view == 'side' else r * 0.9
            ellipse(ctx, kx, y, r * 0.16, r * 0.13)
            fill_stroke(ctx, '#ffffff', lw * 0.7)


def _person_raw(ctx, kind, x, y, s=1.0, facing=1, view='side', phase=0.0, stride=0.0,
                arms=None, reach=None, reach_back=None, sit=False, mouth=0.0, eyes='open',
                bob=0.0, nod=0.0, lean=0.0, hold=None, hold_back=None, legs=None):
    """人物を描く。(x, y) は立ち姿なら足元、座り姿なら座面。

    reach / reach_back: 呼び出し側座標の目標点 (x, y) か (x, y, 重み)。手をそこへ伸ばす。
    hold / hold_back: 手に持たせる描画関数 f(ctx, hx, hy)。
    戻り値: {'front': (x, y), 'back': (x, y)} 呼び出し側座標での手の位置。
    """
    sp = SPECS[kind]
    lw = 4.0

    def to_dev(p):
        if p is None:
            return None
        w = p[2] if len(p) > 2 else 1.0
        return ctx.user_to_device(p[0], p[1]) + (w,)

    rdev, rbdev = to_dev(reach), to_dev(reach_back)

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    hands = {}

    leg = sp['leg']
    th_len, sh_len = leg * 0.5, leg * 0.5
    run = clamp(stride / 1.6)

    # ---- 脚
    if legs is not None:
        leg_ang = legs
    elif sit:
        leg_ang = [(88, 2), (88, 2)]
    else:
        leg_ang = []
        for p in (phase + math.pi, phase):
            th = stride * 26 * math.sin(p)
            kb = stride * 38 * max(0.0, math.sin(p + 1.1))
            leg_ang.append((th, th - kb))
    if sit:
        hip_y = -sp['lw'] * 0.5 + bob
    else:
        ext = max(th_len * dirv(a)[1] + sh_len * dirv(b)[1] for a, b in leg_ang)
        hip_y = -ext - sp['lw'] * 0.6 + bob - run * 6 * abs(math.sin(phase))

    def draw_leg(i, darker):
        a, b = leg_ang[i]
        hx = (-4 if i == 0 else 4) if view == 'side' else (-sp['tw'] * 0.24 if i == 0 else sp['tw'] * 0.24)
        col = sp['pants']
        if view == 'side':
            kx, ky = limb(ctx, hx, hip_y, a, th_len, sp['lw'] * 1.05, col, lw)
            fx, fy = limb(ctx, kx, ky, b, sh_len, sp['lw'], col, lw)
            if kind == 'ryoshi':
                limb(ctx, lerp(kx, fx, 0.45), lerp(ky, fy, 0.45), b, sh_len * 0.55, sp['lw'] * 1.08, sp['shoe'], lw)
            ellipse(ctx, fx + 9, fy + 2, sp['lw'] * 0.85, sp['lw'] * 0.5)
            fill_stroke(ctx, sp['shoe'], lw)
        else:
            if sit:
                # 正面の座り: 腿は手前に短く、すねはぶら下がる
                ellipse(ctx, hx, hip_y + 6, sp['lw'] * 0.8, sp['lw'] * 0.75)
                fill_stroke(ctx, col, lw)
                fx, fy = limb(ctx, hx, hip_y + 12, b, sh_len, sp['lw'], col, lw)
            else:
                fx, fy = limb(ctx, hx, hip_y, 0, leg, sp['lw'] * 1.05, col, lw)
            if kind == 'ryoshi':
                limb(ctx, fx, fy - sh_len * 0.5, 0, sh_len * 0.5, sp['lw'] * 1.08, sp['shoe'], lw)
            ellipse(ctx, fx, fy + 3, sp['lw'] * 0.7, sp['lw'] * 0.5)
            fill_stroke(ctx, sp['shoe'], lw)

    # ---- 胴体の向き
    tlen = sp['torso']
    tw = sp['tw'] if view != 'side' else sp['tw'] * 0.82
    lean_a = lean + run * 12


    # 肩・首の位置（前傾を考慮）
    la = math.radians(lean_a)
    sh_x = math.sin(la) * (tlen - 10)
    sh_y = hip_y - math.cos(la) * (tlen - 10)
    nk_x = math.sin(la) * (tlen + 4)
    nk_y = hip_y - math.cos(la) * (tlen + 4)

    # ---- 腕の角度
    ua, la_ = sp['uarm'], sp['larm']
    if arms is None:
        sw = stride * 28 * math.sin(phase)
        bend = 15 + run * 70
        arms_ = [(sw, sw + bend), (-sw, -sw + bend)] if view == 'side' else [(-8, -4), (8, 4)]
    else:
        arms_ = [tuple(arms[0:2]), tuple(arms[2:4])]

    def shoulder(i):
        if view == 'side':
            return sh_x + (-3 if i == 0 else 3), sh_y
        return sh_x + (-1 if i == 0 else 1) * tw * 0.5, sh_y

    def apply_reach(i, dev):
        if dev is None:
            return
        lx, ly = ctx.device_to_user(dev[0], dev[1])
        sx, sy = shoulder(i)
        a1, a2 = ik2(sx, sy, lx, ly, ua, la_ + sp['lw'] * 0.3, bend=-1 if (view == 'side' or i == 0) else 1)
        w = dev[2]
        o1, o2 = arms_[i]
        arms_[i] = (lerp(o1, a1, w), lerp(o2, a2, w))

    # side: index1 = 手前の腕(front)。front view: index0 = 画面左の腕、index1 = 画面右の腕
    apply_reach(1, rdev)
    apply_reach(0, rbdev)

    def draw_arm(i):
        sx, sy = shoulder(i)
        a1, a2 = arms_[i]
        sleeve = sp['shirt']
        upper = sleeve if kind != 'ryoshi' else SKIN
        lower = SKIN if kind == 'haru' or kind == 'ryoshi' else sp['shirt']
        ex, ey = limb(ctx, sx, sy, a1, ua, sp['lw'] * 0.9, upper, lw)
        if kind == 'ryoshi':
            limb(ctx, sx, sy, a1, ua * 0.45, sp['lw'] * 1.05, sp['shirt'], lw)
        hx, hy = limb(ctx, ex, ey, a2, la_, sp['lw'] * 0.82, lower, lw)
        ellipse(ctx, hx, hy, sp['lw'] * 0.58, sp['lw'] * 0.58)
        fill_stroke(ctx, SKIN, lw)
        key = 'front' if i == 1 else 'back'
        hands[key] = ctx.user_to_device(hx, hy)
        f = hold if i == 1 else hold_back
        if f is not None:
            ctx.save()
            ctx.translate(hx, hy)
            ctx.scale(1 / (s * facing), 1 / s)
            f(ctx, 0, 0)
            ctx.restore()

    # ---- 描画順
    if view == 'side':
        draw_arm(0)
        draw_leg(0, True)
    if view != 'side':
        draw_leg(0, False)
        draw_leg(1, False)
    if view == 'back':
        draw_arm(0)
        draw_arm(1)

    # 胴体
    ctx.save()
    ctx.translate(0, hip_y)
    ctx.rotate(la)
    top = -tlen - 4
    rrect(ctx, -tw / 2, top, tw, tlen + 10, tw * 0.32)
    fill_stroke(ctx, sp['shirt'], lw)
    if kind in ('haru', 'ryoshi'):
        bib = sp['pants']
        bh = tlen * (0.62 if kind == 'haru' else 0.7)
        bw = tw * (0.8 if view != 'side' else 0.7)
        rrect(ctx, -bw / 2, -bh, bw, bh + 10, 8)
        fill_stroke(ctx, bib, lw)
        setc(ctx, OUTLINE)
        ctx.set_line_width(lw)
        if view != 'side':
            for sg in (-1, 1):
                ctx.move_to(sg * bw * 0.32, -bh)
                ctx.line_to(sg * tw * 0.3, top + 8)
                ctx.stroke()
                setc(ctx, bib)
                ctx.set_line_width(lw * 1.6)
                ctx.move_to(sg * bw * 0.32, -bh)
                ctx.line_to(sg * tw * 0.3, top + 8)
                ctx.stroke()
                setc(ctx, OUTLINE)
                ctx.set_line_width(lw)
        else:
            setc(ctx, bib)
            ctx.set_line_width(lw * 2)
            ctx.move_to(0, -bh)
            ctx.line_to(-tw * 0.15, top + 6)
            ctx.stroke()
        if kind == 'haru' and view == 'front':
            rrect(ctx, -bw * 0.2, -bh * 0.75, bw * 0.4, bh * 0.3, 4)
            fill_stroke(ctx, '#5b8bd0', lw * 0.6)
    if kind == 'jii':
        # 手ぬぐい
        ellipse(ctx, 0, top + 6, tw * 0.42, 9)
        fill_stroke(ctx, '#f4f1e8', lw * 0.8)
        setc(ctx, OUTLINE)
        ctx.set_line_width(lw * 0.6)
        ctx.move_to(0, top + 12)
        ctx.line_to(0, -6)
        ctx.stroke()
    if kind == 'haru' and view != 'back':
        ellipse(ctx, 0, top + 4, tw * 0.38, 8)
        fill_stroke(ctx, '#ffffff', lw * 0.8)
    ctx.restore()

    if view == 'side':
        draw_leg(1, False)

    # 頭
    r = sp['head']
    ctx.save()
    ctx.translate(nk_x, nk_y)
    ctx.rotate(math.radians(nod))
    ctx.translate(0, -r * 0.92)
    _head(ctx, kind, sp, view, r, mouth, eyes)
    ctx.restore()

    if view == 'side':
        draw_arm(1)
    elif view == 'front':
        draw_arm(0)
        draw_arm(1)

    ctx.restore()
    out = {}
    for k, v in hands.items():
        out[k] = ctx.device_to_user(*v)
    return out


LIGHT = dict(side=1, shadow='#4f3f86', strength=0.24, rim='#fff0c0', rim_strength=0.22, ground=0.30)


def set_light(**kw):
    """カットごとの光の設定。side: 光が来る側(+1=右, -1=左)"""
    LIGHT.update(dict(side=1, shadow='#4f3f86', strength=0.24, rim='#fff0c0', rim_strength=0.22, ground=0.30))
    LIGHT.update(kw)


def ground_shadow(ctx, x, y, rx, alpha=None, ry=None):
    a = LIGHT['ground'] if alpha is None else alpha
    if _SIL is not None or a <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry or rx * 0.2)
    g = cairo.RadialGradient(0, 0, 0.15, 0, 0, 1)
    g.add_color_stop_rgba(0, 0.12, 0.07, 0.2, a)
    g.add_color_stop_rgba(1, 0.12, 0.07, 0.2, 0)
    ctx.set_source(g)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def draw_person(ctx, kind, x, y, s=1.0, shadow=True, **kw):
    """陰影（セル影＋リムライト）と接地影つきで人物を描く"""
    if _SIL is not None:
        return _person_raw(ctx, kind, x, y, s, **kw)
    sp = SPECS[kind]
    if shadow and not kw.get('sit'):
        ground_shadow(ctx, x, y + 3 * s, sp['tw'] * s * 1.15)
    ctx.push_group()
    hands = _person_raw(ctx, kind, x, y, s, **kw)
    pat = ctx.pop_group()
    ctx.set_source(pat)
    ctx.paint()
    # 横向きの人物は顔の側から光を当てる（表情が暗くならないように）
    side = kw.get('facing', 1) if kw.get('view', 'side') == 'side' else LIGHT['side']
    w = sp['tw'] * s
    top = y - (sp['leg'] + sp['torso'] + sp['head'] * 2) * s
    ctx.save()
    if LIGHT['strength'] > 0:
        r, g_, b, _ = hexc(LIGHT['shadow'])
        ctx.set_operator(cairo.OPERATOR_MULTIPLY)
        g = cairo.LinearGradient(x + side * w * 0.9, top, x - side * w * 0.9, top + w * 0.5)
        g.add_color_stop_rgba(0.0, r, g_, b, 0)
        g.add_color_stop_rgba(0.56, r, g_, b, 0)
        g.add_color_stop_rgba(0.66, r, g_, b, LIGHT['strength'])
        g.add_color_stop_rgba(1.0, r, g_, b, LIGHT['strength'])
        ctx.set_source(g)
        ctx.mask(pat)
        g = cairo.LinearGradient(0, top, 0, y)
        g.add_color_stop_rgba(0.55, r, g_, b, 0)
        g.add_color_stop_rgba(1.0, r, g_, b, LIGHT['strength'] * 0.6)
        ctx.set_source(g)
        ctx.mask(pat)
    if LIGHT['rim_strength'] > 0:
        r, g_, b, _ = hexc(LIGHT['rim'])
        ctx.set_operator(cairo.OPERATOR_ADD)
        g = cairo.LinearGradient(x + side * w * 1.0, top, x - side * w * 0.2, top + w * 0.3)
        g.add_color_stop_rgba(0.0, r, g_, b, LIGHT['rim_strength'])
        g.add_color_stop_rgba(0.35, r, g_, b, LIGHT['rim_strength'] * 0.5)
        g.add_color_stop_rgba(0.6, r, g_, b, 0)
        ctx.set_source(g)
        ctx.mask(pat)
    ctx.restore()
    return hands


def silhouette(color):
    """with silhouette('#2b1d2e'): とするとその間の描画が単色になる"""
    class _S:
        def __enter__(self):
            global _SIL
            self.prev = _SIL
            _SIL = color

        def __exit__(self, *a):
            global _SIL
            _SIL = self.prev
    return _S()


# ---------------------------------------------------------------- 自然物


class Tree:
    def __init__(self, rng, x, y, size):
        self.x, self.y, self.size = x, y, size
        self.blobs = [(rng.uniform(-0.75, 0.75), rng.uniform(-1.25, -0.55), rng.uniform(0.35, 0.55)) for _ in range(7)]
        self.fruits = [(rng.uniform(-0.75, 0.75), rng.uniform(-1.3, -0.45)) for _ in range(rng.randint(6, 11))]
        self.ph = rng.uniform(0, 6.28)

    def draw(self, ctx, t=0.0, lw=None, dark='#2f6b3a', light='#4f9445'):
        s = self.size
        lw = lw if lw is not None else max(1.5, s * 0.035)
        sway = math.sin(t * 1.3 + self.ph) * s * 0.02
        ctx.save()
        ctx.translate(self.x, self.y)
        limb(ctx, 0, 0, 180, s * 0.45, s * 0.12, '#6b4a33', lw)
        for bx, by, br in self.blobs:
            ellipse(ctx, bx * s + sway, by * s * 0.85, br * s, br * s * 0.9)
            fill_stroke(ctx, dark, lw)
        for bx, by, br in self.blobs[:4]:
            ellipse(ctx, bx * s * 0.9 + sway - br * s * 0.15, by * s * 0.85 - br * s * 0.2, br * s * 0.55, br * s * 0.45)
            setc(ctx, light)
            ctx.fill()
        for fx, fy in self.fruits:
            ellipse(ctx, fx * s + sway, fy * s * 0.85, s * 0.075, s * 0.07)
            fill_stroke(ctx, ORANGE, lw * 0.7)
        ctx.restore()


class Clouds:
    def __init__(self, seed, n, ymin, ymax, smin, smax):
        rng = random.Random(seed)
        self.items = []
        for _ in range(n):
            x, y, s = rng.uniform(-200, W + 200), rng.uniform(ymin, ymax), rng.uniform(smin, smax)
            puffs = [(rng.uniform(-1.2, 1.2), rng.uniform(-0.5, 0.0), rng.uniform(0.35, 0.6)) for _ in range(6)]
            self.items.append((x, y, s, puffs, rng.uniform(6, 14)))

    def draw(self, ctx, t, color='#ffffff', alpha=0.9):
        for x, y, s, puffs, v in self.items:
            xx = (x + v * t + 300) % (W + 600) - 300
            ctx.push_group()
            setc(ctx, color)
            for px, py, pr in puffs:
                ellipse(ctx, xx + px * s, y + py * s, pr * s * 1.3, pr * s)
                ctx.fill()
            rrect(ctx, xx - 1.4 * s, y - 0.1 * s, 2.8 * s, 0.3 * s, 0.15 * s)
            ctx.fill()
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(alpha)


def sky(ctx, stops, y0=0, y1=H):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for off, c in stops:
        g.add_color_stop_rgb(off, *hexc(c)[:3])
    ctx.set_source(g)
    ctx.rectangle(-W, -H, W * 3, H * 3)
    ctx.fill()


def sea(ctx, y0, y1, top, bottom, t=0.0, x0=-W, x1=2 * W, lines=True, line_color='#ffffff', line_alpha=0.22, seed=3):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *hexc(top)[:3])
    g.add_color_stop_rgb(1, *hexc(bottom)[:3])
    ctx.set_source(g)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.fill()
    if lines:
        rng = random.Random(seed)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for _ in range(60):
            yy = rng.uniform(y0 + 4, y1)
            f = (yy - y0) / max(1, (y1 - y0))
            ln = rng.uniform(20, 70) * (0.4 + f * 1.6)
            xx = rng.uniform(x0, x1) + math.sin(t * 0.5 + yy) * 12
            setc(ctx, line_color, line_alpha)
            ctx.set_line_width(1.2 + f * 3)
            ctx.move_to(xx, yy)
            ctx.line_to(xx + ln, yy)
            ctx.stroke()


def islands(ctx, y, color, seed=5, x0=-100, x1=W + 100):
    rng = random.Random(seed)
    x = x0 + rng.uniform(0, 300)
    while x < x1:
        w = rng.uniform(160, 420)
        h = rng.uniform(18, 55)
        ctx.move_to(x, y)
        ctx.curve_to(x + w * 0.25, y - h, x + w * 0.65, y - h * 1.1, x + w, y)
        ctx.close_path()
        setc(ctx, color)
        ctx.fill()
        x += w + rng.uniform(150, 600)


def stone_wall(ctx, x, y, w, h, seed, base='#bdb3a2', dark='#8f8473', light='#d6ceBF', block=None):
    """石垣（ブロック模様）"""
    rng = random.Random(seed)
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    setc(ctx, base)
    ctx.paint()
    bh = block or max(10, min(46, h / 3))
    yy = y
    while yy < y + h:
        xx = x - rng.uniform(0, bh * 1.6)
        while xx < x + w:
            bw = rng.uniform(bh * 1.1, bh * 2.0)
            rrect(ctx, xx + 2, yy + 2, bw - 4, bh - 4, bh * 0.3)
            c = mixc(light, base, rng.uniform(0, 1))
            ctx.set_source_rgb(*c)
            ctx.fill_preserve()
            setc(ctx, dark)
            ctx.set_line_width(max(1.0, bh * 0.07))
            ctx.stroke()
            xx += bw
        yy += bh
    ctx.restore()


def house(ctx, x, y, w, h, wall='#efe6d6', roof='#4b5a70', seed=0, window=True, lw=3.0):
    """(x, y) は家の左下"""
    rng = random.Random(seed)
    ctx.rectangle(x, y - h, w, h)
    fill_stroke(ctx, wall, lw)
    if h > 60:
        ctx.rectangle(x, y - h * 0.38, w, h * 0.38)
        fill_stroke(ctx, '#8a6a4a', lw)
        setc(ctx, '#6e523a')
        ctx.set_line_width(max(1, lw * 0.5))
        bx = x + 10
        while bx < x + w:
            ctx.move_to(bx, y - h * 0.38)
            ctx.line_to(bx, y)
            ctx.stroke()
            bx += 14
    if window:
        n = max(1, int(w // 90))
        for i in range(n):
            wx = x + (i + 0.5) * w / n - w * 0.12
            ctx.rectangle(wx, y - h * 0.8, w * 0.24, h * 0.26)
            fill_stroke(ctx, '#9cc3d8' if rng.random() > 0.3 else '#f3dca0', lw * 0.8)
    rh = h * 0.35
    ctx.move_to(x - w * 0.08, y - h)
    ctx.line_to(x + w * 0.5, y - h - rh)
    ctx.line_to(x + w * 1.08, y - h)
    ctx.close_path()
    fill_stroke(ctx, roof, lw)
    setc(ctx, '#3a4659')
    ctx.set_line_width(max(1, lw * 0.6))
    for i in range(1, 6):
        f = i / 6
        ctx.move_to(lerp(x - w * 0.08, x + w * 0.5, f), lerp(y - h, y - h - rh, f))
        ctx.line_to(lerp(x + w * 1.08, x + w * 0.5, f), lerp(y - h, y - h - rh, f))
        ctx.stroke()


def boat(ctx, x, y, s, t=0.0, ph=0.0, hull='#fbfbf7', stripe='#2f6db5', lw=3.0):
    bob = math.sin(t * 1.4 + ph) * 4 * s
    tilt = math.sin(t * 1.1 + ph) * 0.02
    ctx.save()
    ctx.translate(x, y + bob)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    # マスト
    limb(ctx, -40, -40, 180, 120, 5, '#d8d8d8', lw)
    setc(ctx, '#d8d8d8')
    ctx.set_line_width(2)
    ctx.move_to(-40, -160)
    ctx.line_to(90, -45)
    ctx.stroke()
    # 操舵室
    rrect(ctx, 0, -95, 70, 60, 8)
    fill_stroke(ctx, '#fbfbf7', lw)
    ctx.rectangle(10, -85, 50, 18)
    fill_stroke(ctx, '#7fb3d5', lw * 0.8)
    # 船体
    ctx.move_to(-130, -40)
    ctx.line_to(150, -40)
    ctx.line_to(120, 10)
    ctx.line_to(-110, 10)
    ctx.close_path()
    fill_stroke(ctx, hull, lw)
    ctx.rectangle(-122, -20, 262, 10)
    setc(ctx, stripe)
    ctx.fill()
    ctx.restore()


def gull(ctx, x, y, s, t, ph=0.0, color='#ffffff'):
    flap = math.sin(t * 2.2 + ph) * 0.35
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    setc(ctx, OUTLINE)
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sg in (-1, 1):
        ctx.move_to(0, 0)
        ctx.curve_to(sg * 12, -10 - flap * 20, sg * 24, -8 - flap * 20, sg * 34, 2 - flap * 25)
        ctx.stroke()
    ctx.restore()


def cat(ctx, x, y, s, pose=0.0, eyes='closed', facing=1):
    """塀の上の猫。pose: 0=丸まり, 1=びっくり（背を丸めて立つ）"""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    lw = 3.0
    body_h = lerp(26, 34, pose)
    by = -lerp(22, 42, pose)
    # しっぽ
    setc(ctx, OUTLINE)
    ctx.set_line_width(12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-38, by + 8)
    ctx.curve_to(-70, by - 10 - pose * 40, -60, by - 40 - pose * 30, -50 + pose * 5, by - 50 - pose * 25)
    ctx.stroke_preserve()
    setc(ctx, '#f6f1e6')
    ctx.set_line_width(7)
    ctx.stroke()
    if pose > 0.2:
        for lx in (-26, -14, 18, 30):
            limb(ctx, lx, by + 10, 0, lerp(8, 34, pose), 9, '#f6f1e6', lw)
    # 胴
    ctx.move_to(-44, by + 14)
    ctx.curve_to(-44, by - body_h - pose * 22, 40, by - body_h - pose * 22, 40, by + 14)
    ctx.close_path()
    fill_stroke(ctx, '#f6f1e6', lw)
    ellipse(ctx, -14, by - body_h * 0.45 - pose * 10, 14, 9)
    setc(ctx, '#e39a4c')
    ctx.fill()
    ellipse(ctx, 12, by - body_h * 0.2 - pose * 8, 10, 7)
    setc(ctx, '#3a3030')
    ctx.fill()
    # 頭
    hx, hy = 40, by - 6 - pose * 22
    for ex in (-12, 10):
        ctx.move_to(hx + ex - 7, hy - 12)
        ctx.line_to(hx + ex, hy - 30 - pose * 4)
        ctx.line_to(hx + ex + 8, hy - 12)
        ctx.close_path()
        fill_stroke(ctx, '#f6f1e6', lw)
    ellipse(ctx, hx, hy, 22, 19)
    fill_stroke(ctx, '#f6f1e6', lw)
    ellipse(ctx, hx - 8, hy - 9, 9, 6)
    setc(ctx, '#e39a4c')
    ctx.fill()
    if eyes == 'closed':
        setc(ctx, OUTLINE)
        ctx.set_line_width(2.5)
        for ex in (-7, 9):
            ctx.arc(hx + ex, hy - 1, 4, 0.1 * math.pi, 0.9 * math.pi)
            ctx.stroke()
    else:
        for ex in (-7, 9):
            ellipse(ctx, hx + ex, hy - 2, 4.5, 6.5)
            setc(ctx, '#231a1e')
            ctx.fill()
    ctx.restore()


def bounce_path(top, x0, y0, vx, dur, r, g=2600.0, rest=0.42, dt=1 / 600, vy0=0.0):
    """段差 top(x) の上を転がる玉の軌跡。[(t, x, y, rot)] と着地時刻を返す。"""
    out, hits = [], []
    x, y, vy, rot, t = x0, y0, vy0, 0.0, 0.0
    on_ground = False
    n = int(dur / dt) + 2
    for i in range(n):
        t = i * dt
        out.append((t, x, y, rot))
        x += vx * dt
        rot += vx * dt / r
        floor = top(x) - r
        if on_ground and y < floor - 0.5:
            on_ground = False
        if not on_ground:
            vy += g * dt
            y += vy * dt
            if y >= floor:
                y = floor
                if vy > 260:
                    hits.append((t, min(1.0, vy / 1400)))
                    vy = -vy * rest
                else:
                    vy = 0
                    on_ground = True
        else:
            y = floor
    return out, hits


def sample_path(path, t, dt=1 / 600):
    i = int(clamp(t / dt, 0, len(path) - 1))
    return path[i]
