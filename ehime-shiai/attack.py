#!/usr/bin/env python3
"""守備側のユニフォームの色から、どちらのチームが攻撃中かを時系列で推定する。

    python3 attack.py footage/00002.MTS

中田ジャパンは赤、八幡浜は白。グラウンド部分（画面の中段）に映る赤い画素の割合を
5秒ごとに出す。赤が多い = 中田が守備 = 八幡浜の攻撃。
"""
import subprocess
import sys

import numpy as np

W, H, STEP = 320, 180, 5


def main():
    path = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0",
                          "-vf", f"yadif,fps=1/{STEP},scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    n = W * H * 3
    i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16)
        band = f[int(H * 0.22):int(H * 0.45)]          # 外野〜内野の奥（打者・走者の多い本塁付近は除く）
        r, g, bl = band[..., 0], band[..., 1], band[..., 2]
        red = (r > 110) & (r - g > 45) & (r - bl > 35)
        t = i * STEP
        print(f"{t // 60:3d}:{t % 60:02d} {red.mean() * 1000:6.2f}")
        i += 1
    p.wait()


if __name__ == "__main__":
    main()
