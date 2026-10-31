#!/usr/bin/env python3
"""素材ごとの手ブレ量を測る（位相相関でフレーム間の平行移動を推定）。

    python3 shake.py footage/*.mov

jitter: 動きの細かい揺れ成分（px/フレーム, 1920幅換算）。パンなどのゆっくりした動きは除く。
1秒ごとの jitter も出すので、揺れの少ない区間を選ぶのに使う。
"""
import subprocess
import sys

import numpy as np

W, H = 320, 180


def frames(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).astype(np.float32)


def shift(a, b, win):
    fa, fb = np.fft.fft2(a * win), np.fft.fft2(b * win)
    r = fa * np.conj(fb)
    c = np.fft.ifft2(r / (np.abs(r) + 1e-6)).real
    y, x = np.unravel_index(np.argmax(c), c.shape)
    return (x if x < W // 2 else x - W), (y if y < H // 2 else y - H)


def smooth(x, k=15):
    return np.convolve(np.pad(x, k // 2, mode="edge"), np.ones(k) / k, mode="valid")


for path in sys.argv[1:]:
    f = frames(path)
    win = np.outer(np.hanning(H), np.hanning(W))
    d = np.array([shift(f[i + 1], f[i], win) for i in range(len(f) - 1)], float) * (1920 / W)
    jit = np.hypot(d[:, 0] - smooth(d[:, 0]), d[:, 1] - smooth(d[:, 1]))
    per_sec = [jit[i:i + 30].mean() for i in range(0, len(jit), 30)]
    print(f"{path}: jitter平均 {jit.mean():.2f}px  最大1秒 {max(per_sec):.2f}px")
    print("   1秒ごと:", " ".join(f"{v:.1f}" for v in per_sec))
