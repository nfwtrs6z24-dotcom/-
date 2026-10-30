#!/usr/bin/env python3
"""開会式用オリジナルBGM（128BPM・Dマイナーの行進系ロック）を合成する。

    python3 bgm.py 60 bgm.wav     # 約60秒に合わせて生成（最後はキメの一発で終わる）

構成: イントロ(ビルド4小節) → A(ドラム+ベース+コード) → B(メロディ追加) → キメ+余韻
指定秒数に合わせて A/B の小節数を伸び縮みさせる。
"""
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
BPM = 128
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(33)


def t_arr(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def supersaw(f, dur, voices=5, detune=0.012):
    t = t_arr(dur)
    out = sum(saw(f * (1 + detune * (v - voices // 2) / voices), t + rng.random() / f)
              for v in range(voices))
    return out / voices


# ---- ドラム ---------------------------------------------------------------
def kick():
    t = t_arr(0.45)
    f = 50 + 120 * np.exp(-t * 35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 300) * 0.3
    return np.tanh((body + click) * 1.8) * 0.9


def snare():
    t = t_arr(0.35)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.5
    noise = hp(lp(rng.standard_normal(len(t)), 9000), 900) * np.exp(-t * 14)
    return np.tanh((tone + noise) * 1.5) * 0.7


def hat(open_=False):
    t = t_arr(0.3 if open_ else 0.06)
    return hp(rng.standard_normal(len(t)), 7000, 4) * np.exp(-t * (12 if open_ else 70)) * 0.12


def tom(f0):
    t = t_arr(0.4)
    f = f0 * (1 + 0.5 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) * 0.7


def crash():
    t = t_arr(2.5)
    return lp(hp(rng.standard_normal(len(t)), 3000), 11000) * np.exp(-t * 1.8) * 0.18


def timpani(f0, dur=3.0):
    t = t_arr(dur)
    x = sum(np.sin(2 * np.pi * f0 * m * t) * a for m, a in [(1, 1), (1.5, .4), (2, .25)])
    x += lp(rng.standard_normal(len(t)), 400) * 0.6 * np.exp(-t * 20)
    return np.tanh(x * np.exp(-t * 1.5) * 1.5) * 0.8


# ---- 曲 -------------------------------------------------------------------
# Dm - B♭ - F - C（王道の熱いマイナー進行）。ルートのMIDIノート番号
PROG = [(50, "m"), (46, ""), (53, ""), (48, "")]


def chord_notes(root, q):
    third = 3 if q == "m" else 4
    return [root, root + third, root + 7, root + 12]


# メロディ（2小節×4 = 8小節の動機）。(拍位置, 長さ拍, MIDI)
MELODY = [
    (0, 1.5, 74), (1.5, .5, 76), (2, 1, 77), (3, 1, 76),
    (4, 2, 74), (6, 1, 69), (7, 1, 72),
    (8, 1.5, 70), (9.5, .5, 72), (10, 1, 74), (11, 1, 77),
    (12, 3, 77), (15, 1, 76),
    (16, 1.5, 72), (17.5, .5, 74), (18, 1, 76), (19, 1, 77),
    (20, 2, 79), (22, 1, 77), (23, 1, 76),
    (24, 1.5, 74), (25.5, .5, 76), (26, 1, 77), (27, 1, 79),
    (28, 4, 81),
]


class Mix:
    def __init__(self, dur):
        self.L = np.zeros(int(dur * SR) + SR * 4)
        self.R = np.zeros_like(self.L)

    def add(self, x, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        x = x[: len(self.L) - i]
        self.L[i:i + len(x)] += x * gain * np.sqrt((1 - pan) / 2) * 1.414
        self.R[i:i + len(x)] += x * gain * np.sqrt((1 + pan) / 2) * 1.414


def pad(notes, dur):
    x = sum(supersaw(hz(n), dur, 7, 0.02) for n in notes) / len(notes)
    return lp(x, 2200) * env(len(x), 0.3, 0.4)


def stab(notes, dur):
    x = sum(supersaw(hz(n), dur, 5, 0.015) for n in notes) / len(notes)
    t = t_arr(dur)
    return lp(x, 3500) * env(len(x), 0.004, 0.05) * (0.6 + 0.4 * np.exp(-t * 6))


def bass(note, dur):
    t = t_arr(dur)
    x = saw(hz(note), t) * 0.6 + np.sin(2 * np.pi * hz(note) * t)
    return np.tanh(lp(x, 900) * 1.5) * env(len(t), 0.003, 0.03) * 0.55


def lead(note, dur):
    t = t_arr(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1)
    ph = np.cumsum(hz(note) * vib) / SR
    x = (2 * (ph % 1) - 1) * 0.5 + (np.abs(2 * (ph * 2 % 1) - 1) - .5) * 0.4
    x = lp(x, 3200) * env(len(t), 0.03, 0.08)
    return np.tanh(x * 1.6) * 0.5


def riser(dur):
    t = t_arr(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    for k in range(8):  # 帯域を徐々に上げる
        seg = slice(k * len(t) // 8, (k + 1) * len(t) // 8)
        out[seg] = hp(n, 200 + 900 * k)[seg]
    return out * (t / dur) ** 2 * 0.35


def compose(target):
    intro_bars, end_tail = 4, 3.0
    body = max(8, int(np.ceil((target - end_tail - intro_bars * BAR) / BAR / 4)) * 4)
    a_bars = max(4, (body // 2) // 4 * 4)
    b_bars = body - a_bars
    total_bars = intro_bars + a_bars + b_bars
    end_t = total_bars * BAR
    m = Mix(end_t + end_tail)

    K, S, OH = kick(), snare(), hat(True)

    # イントロ: パッド＋ティンパニ＋タム連打で溜める
    for b in range(intro_bars):
        root, q = PROG[b % 4]
        m.add(pad(chord_notes(root, q), BAR), b * BAR, 0.35)
        m.add(timpani(hz(root - 24), 1.2), b * BAR, 0.6)
    for i in range(16):  # 最後の1小節を16分のタムロール
        m.add(tom([180, 150, 120, 95][i // 4]), (intro_bars - 1) * BAR + i * BEAT / 4,
              0.35 + 0.03 * i, pan=[-.4, -.1, .1, .4][i // 4])
    m.add(riser(BAR * 2), (intro_bars - 2) * BAR, 0.8)

    # 本編
    for b in range(a_bars + b_bars):
        bar_t = (intro_bars + b) * BAR
        root, q = PROG[b % 4]
        notes = chord_notes(root, q)
        in_b = b >= a_bars
        if b % 8 == 0:
            m.add(crash(), bar_t, 0.9, 0.3)
        for beat in range(4):
            bt = bar_t + beat * BEAT
            m.add(K, bt, 1.0)
            if beat in (1, 3):
                m.add(S, bt, 0.9, 0.05)
            for h in range(2):
                m.add(hat(), bt + h * BEAT / 2, 0.8 if h else 0.5, 0.35)
            m.add(OH, bt + BEAT * 0.75, 0.25, -0.3)
        # 小節終わりのスネアフィル（4小節ごと）
        if b % 4 == 3:
            for i in range(4):
                m.add(S, bar_t + 3 * BEAT + i * BEAT / 4, 0.4 + 0.12 * i)
        # 8分ベース
        for e in range(8):
            n = root - 12 + (12 if e in (3, 7) else 0)
            m.add(bass(n, BEAT / 2 * 0.9), bar_t + e * BEAT / 2, 0.9)
        # シンセのキメ（裏拍で刻む）
        for e, ln in [(0, .75), (1.5, .5), (2.5, .5), (3, .75)]:
            m.add(stab(notes, BEAT * ln), bar_t + e * BEAT, 0.28 if not in_b else 0.22, -0.25)
            m.add(stab([n + 12 for n in notes[:3]], BEAT * ln), bar_t + e * BEAT, 0.12, 0.35)
        m.add(pad(notes, BAR), bar_t, 0.18 if not in_b else 0.24)
        # Bセクション: メロディ
        if in_b:
            off = ((b - a_bars) % 8) * 4
            for pos, ln, note in MELODY:
                if off <= pos < off + 4:
                    t0 = bar_t + (pos - off) * BEAT
                    m.add(lead(note, ln * BEAT * 0.95), t0, 0.45, -0.05)
                    m.add(lead(note - 12, ln * BEAT * 0.95), t0, 0.2, 0.15)
    m.add(riser(BAR), end_t - BAR, 0.6)

    # キメの一発（Dm）＋余韻
    m.add(K, end_t, 1.2)
    m.add(timpani(hz(38), end_tail), end_t, 0.9)
    m.add(crash(), end_t, 1.2)
    m.add(pad(chord_notes(50, "m") + [62, 69], end_tail), end_t, 0.6)
    m.add(stab(chord_notes(50, "m"), 0.4), end_t, 0.6)

    # リバーブ（ノイズ減衰のIRを畳み込み）
    ir_t = t_arr(1.6)
    irL = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 4)
    irR = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 4)
    irL, irR = lp(irL, 5000) / np.sqrt(np.sum(irL ** 2)), lp(irR, 5000) / np.sqrt(np.sum(irR ** 2))
    L = m.L + 0.18 * fftconvolve(m.L, irL)[: len(m.L)]
    R = m.R + 0.18 * fftconvolve(m.R, irR)[: len(m.R)]
    st = np.stack([L, R], 1)[: int((end_t + end_tail) * SR)]
    st = hp(st.T, 30).T
    st = np.tanh(st / np.max(np.abs(st)) * 1.1)  # 軽くサチュレーションで音圧を出す
    st = st / np.max(np.abs(st)) * 0.93
    fade = int(0.8 * SR)
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return st, end_t + end_tail


def write_wav(path, st):
    import wave
    data = (st * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    target = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    out = sys.argv[2] if len(sys.argv) > 2 else "bgm.wav"
    st, dur = compose(target)
    write_wav(out, st)
    print(f"{out}: {dur:.2f}s  (キメの位置 {dur - 3.0:.2f}s)")
