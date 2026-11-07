#!/usr/bin/env python3
"""試合映像から見どころ候補を探す（固定カメラ向け）。

    python3 analyze.py footage/00002.MTS [...]

0.5秒ごとに
  loud : 音の大きさ (dB)。歓声・声援・打球音で上がる
  hit  : 1〜4kHz の短い立ち上がり。打球音（カーン）の手がかり
  move : 画面の動き量。打球・走塁・守備で上がる
を計算し、<名前>.csv に書き出す。あわせて動き＋音が大きい区間を候補として表示する。
"""
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np

STEP = 0.5          # 秒
W, H, FPS = 192, 108, 4
SR = 16000


def audio(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                        "-f", "s16le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.int16).astype(np.float32) / 32768


def motion(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0",
                          "-vf", f"yadif,fps={FPS},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    prev, out = None, []
    n = W * H
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        f = np.frombuffer(b, np.uint8).astype(np.float32)
        out.append(0.0 if prev is None else float(np.mean(np.abs(f - prev) > 12)))
        prev = f
    p.wait()
    m = np.array(out)
    k = int(FPS * STEP)
    return m[: len(m) // k * k].reshape(-1, k).mean(1)


def bandpass_energy(a):
    # 1〜4kHz 帯のエネルギー（FFTで簡易に）
    k = int(SR * 0.05)
    a = a[: len(a) // k * k].reshape(-1, k)
    spec = np.abs(np.fft.rfft(a * np.hanning(k), axis=1))
    f = np.fft.rfftfreq(k, 1 / SR)
    return spec[:, (f > 1000) & (f < 4000)].sum(1)


def main():
    for path in sys.argv[1:]:
        a = audio(path)
        k = int(SR * STEP)
        a2 = a[: len(a) // k * k].reshape(-1, k)
        loud = 20 * np.log10(np.sqrt((a2 ** 2).mean(1)) + 1e-9)
        be = bandpass_energy(a)                       # 50ms ごと
        onset = np.maximum(0, be[1:] - np.maximum(be[:-1], 1e-9) * 3)  # 急な立ち上がり
        onset = np.concatenate([[0], onset])
        per = int(STEP / 0.05)
        hit = onset[: len(onset) // per * per].reshape(-1, per).max(1)
        mv = motion(path)
        n = min(len(loud), len(hit), len(mv))
        loud, hit, mv = loud[:n], hit[:n], mv[:n]
        out = Path(path).with_suffix(".csv").name
        with open(Path(path).parent.parent / "work" / out, "w", newline="") as fp:
            w = csv.writer(fp)
            w.writerow(["t", "loud", "hit", "move"])
            for i in range(n):
                w.writerow([f"{i * STEP:.1f}", f"{loud[i]:.1f}", f"{hit[i]:.3f}", f"{mv[i]:.4f}"])
        # 候補: 動きと音の z スコアの和が大きい区間（10秒以上離す）
        z = lambda x: (x - np.median(x)) / (np.std(x) + 1e-9)
        sm = lambda x, k=6: np.convolve(x, np.ones(k) / k, mode="same")
        score = sm(z(mv)) + 0.7 * sm(z(loud)) + 0.3 * sm(z(np.log1p(hit)))
        picks = []
        for i in np.argsort(score)[::-1]:
            if all(abs(i - j) * STEP > 10 for j in picks):
                picks.append(i)
            if len(picks) >= 25:
                break
        print(f"== {path}  ({n * STEP / 60:.1f}分)")
        for i in sorted(picks):
            t = i * STEP
            print(f"  {int(t // 60):3d}:{t % 60:04.1f}  score {score[i]:.2f}  move {mv[i]:.3f}  loud {loud[i]:.0f}dB")


if __name__ == "__main__":
    main()
