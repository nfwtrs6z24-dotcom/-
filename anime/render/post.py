"""仕上げ（撮影処理）: 光のにじみ・フィルムグレイン・モーションブラー"""
import numpy as np
from PIL import Image, ImageFilter

from common import W, H

_rng = np.random.default_rng(7)
_GRAIN = [np.clip(_rng.normal(0, 2.6, (H, W, 1)), -8, 8).astype(np.int16) for _ in range(4)]

LOOKS = {
    'default': dict(glow=0.22, soft=0.06, thr=185, radius=7),
    'S06': dict(glow=0.24, soft=0.07, thr=190, radius=8),
    'S07': dict(glow=0.26, soft=0.08, thr=190, radius=8),
    'S08': dict(glow=0.26, soft=0.08, thr=190, radius=8),
    'S09': dict(glow=0.55, soft=0.12, thr=150, radius=11),
    'S10': dict(glow=0.45, soft=0.10, thr=150, radius=9),
}


def finish(rgb, idx, name):
    """rgb: (H, W, 3) uint8 → 仕上げ済みの uint8"""
    lk = LOOKS.get(name, LOOKS['default'])
    small = np.asarray(Image.fromarray(rgb).reduce(4)).astype(np.float32)
    lum = small.max(axis=2, keepdims=True)
    k = np.clip((lum - lk['thr']) / (255.0 - lk['thr']), 0, 1) * lk['glow'] + lk['soft']
    glow = Image.fromarray(np.clip(small * k, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(lk['radius']))
    glow = np.asarray(glow.resize((W, H), Image.BILINEAR)).astype(np.uint16)
    base = rgb.astype(np.uint16)
    out = base + (glow * (255 - base) >> 8)          # スクリーン合成
    out = out.astype(np.int16) + _GRAIN[idx % 4]
    return np.clip(out, 0, 255).astype(np.uint8)


def render_frame(shot, surf, cairo, t, dt, idx, name):
    """モーションブラー（SUB 回描いて平均）＋仕上げをかけた1フレームの BGR0 バイト列"""
    sub = getattr(shot, 'SUB', 1)
    acc = None
    for k in range(sub):
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        shot.draw(ctx, max(0.0, t + ((k + 0.5) / sub - 0.5) * 0.6 * dt))
        surf.flush()
        a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[:, :, :3]
        if sub == 1:
            acc = a.copy()
        else:
            acc = a.astype(np.uint16) if acc is None else acc + a
    if sub > 1:
        acc = (acc // sub).astype(np.uint8)
    out = np.empty((H, W, 4), np.uint8)
    out[:, :, :3] = finish(acc, idx, name)
    out[:, :, 3] = 255
    return out
