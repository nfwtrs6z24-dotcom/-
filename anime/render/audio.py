"""音づくり: 仮ボイス(Open JTalk)・オリジナルBGM・効果音を生成する。

出力: ../audio/voice.wav, ../audio/bgm.wav, ../audio/se.wav, voice_timing.json
BGM・効果音はすべてこのプログラムで合成したオリジナル（外部音源なし）。
"""
import json
import math
import os
import random
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'audio')
SR = 48000
TOTAL = 60.0
N = int(SR * TOTAL)

# ---------------------------------------------------------------- 共通


def write_wav(path, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    y = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())


def lowpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, fc):
    return x - lowpass(x, fc)


def place(buf, sig, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    if buf.ndim == 2 and sig.ndim == 1:
        buf[i:j] += sig[:j - i, None] * gain
    else:
        buf[i:j] += sig[:j - i] * gain


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- 声（仮ボイス）

LINES = [
    # who, 開始秒, テキスト, half_tone, speed
    ('na', 1.0, '海と山のあいだの町、八幡浜。', 0.0, 0.92),
    ('haru', 7.0, '見て！ こんなに大きいよ！', 6.0, 1.05),
    ('haru', 10.85, 'あっ！', 6.0, 1.0),
    ('haru', 15.0, 'まってー！', 6.0, 1.0),
    ('ryoshi', 32.0, 'ええみかんじゃねえ。', -2.0, 0.9),
    ('haru', 37.6, 'はんぶんこ、しよ。', 6.0, 1.0),
    ('na', 45.2, 'ころがった先で、だれかと、つながる。', 0.0, 0.85),
]


def make_voice():
    import pyopenjtalk
    buf = np.zeros(N)
    timing = []
    for who, start, text, ht, sp in LINES:
        x, sr = pyopenjtalk.tts(text, speed=sp, half_tone=ht)
        x = np.asarray(x, dtype=np.float64) / 32768.0
        if sr != SR:
            idx = np.arange(0, len(x), sr / SR)
            x = np.interp(idx, np.arange(len(x)), x)
        # 前後の無音を削る
        env = np.abs(x) > 0.01
        nz = np.nonzero(env)[0]
        x = x[max(0, nz[0] - 480):nz[-1] + 2400]
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
        fade = np.minimum(1, np.arange(len(x)) / 240)
        x *= fade * fade[::-1]
        place(buf, x, start)
        timing.append(dict(who=who, start=start, dur=round(len(x) / SR - 0.05, 3), text=text))
        print(f'  voice {who:6s} {start:5.2f}s +{len(x) / SR:4.2f}s  {text}')
    write_wav(os.path.join(OUT, 'voice.wav'), buf)
    with open(os.path.join(HERE, 'voice_timing.json'), 'w') as f:
        json.dump(dict(lines=timing), f, ensure_ascii=False, indent=1)
    return buf, timing


# ---------------------------------------------------------------- BGM（オリジナル曲）

BEAT = 0.75  # 80 BPM
BAR = BEAT * 4  # 20小節 = 60秒

CHORDS = {
    'F': (41, [53, 57, 60, 65, 69]), 'C': (36, [48, 55, 60, 64, 67]), 'C/E': (40, [48, 55, 60, 64, 67]),
    'Dm': (38, [50, 57, 62, 65, 69]), 'Bb': (46, [46, 53, 58, 62, 65]), 'Gm': (43, [55, 58, 62, 67, 70]),
    'Am': (45, [57, 60, 64, 69, 72]),
}
PROG = ['F', 'C/E', 'Dm', 'Bb',            # 0-12s   朝の段々畑
        'F', 'C', 'Dm', 'C',               # 12-24s  追いかけっこ
        'Bb', 'F', 'Gm', 'C', 'Am', 'Dm',  # 24-42s  港
        'Bb', 'C', 'Bb',                   # 42-51s  夕日
        'F', 'F', 'F']                     # 51-60s  タイトル
MELODY = {  # 小節: [(拍, MIDI, 長さ拍)]
    4: [(0, 72, .5), (.5, 74, .5), (1, 77, .5), (1.5, 74, .5), (2, 72, .5), (2.5, 69, .5), (3, 72, 1)],
    5: [(0, 67, .5), (.5, 69, .5), (1, 72, .5), (1.5, 69, .5), (2, 67, .5), (2.5, 64, .5), (3, 67, 1)],
    6: [(0, 69, .5), (.5, 72, .5), (1, 74, .5), (1.5, 72, .5), (2, 69, .5), (2.5, 74, .5), (3, 77, .5), (3.5, 79, .5)],
    7: [(0, 76, .5), (.5, 74, .5), (1, 72, .5), (1.5, 74, .5), (2, 76, 1), (3, 79, 1)],
    8: [(0, 74, 1), (1, 72, 1), (2, 70, 2)],
    9: [(0, 69, 1), (1, 72, 1), (2, 77, 2)],
    10: [(0, 74, 1), (1, 72, 1), (2, 70, 1), (3, 67, 1)],
    11: [(0, 72, 2), (2, 76, 2)],
    12: [(0, 76, 1), (1, 74, 1), (2, 72, 2)],
    13: [(0, 69, 1), (1, 72, 1), (2, 74, 2)],
    14: [(0, 77, 2), (2, 74, 1), (3, 77, 1)],
    15: [(0, 79, 2), (2, 76, 1), (3, 72, 1)],
    16: [(0, 74, 1), (1, 76, 1), (2, 79, 2)],
    17: [(0, 77, 4)],
}


def piano(f, dur, vel=0.5):
    n = int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > SR / 2.2:
            break
        x += (1 / k ** 1.4) * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + 0.55 * k))
    att = np.minimum(1, t / 0.004)
    rel = np.where(t < dur, 1.0, np.exp(-(t - dur) * 6))
    return x * att * rel * vel


def pluck(f, dur, vel=0.4, seed=0):
    """カープラス・ストロング法のギター風の音"""
    n = int((dur + 0.8) * SR)
    p = max(2, int(SR / f))
    rng = np.random.default_rng(seed)
    buf = lowpass(rng.uniform(-1, 1, p * 8), 3500)[:p]
    out = np.zeros(n)
    # ブロック単位で平均化（ループを短くする）
    cur = buf.copy()
    i = 0
    while i < n:
        m = min(p, n - i)
        out[i:i + m] = cur[:m]
        cur = 0.996 * 0.5 * (cur + np.roll(cur, -1))
        i += p
    t = np.arange(n) / SR
    rel = np.where(t < dur, 1.0, np.exp(-(t - dur) * 8))
    return out * rel * vel


def bass(f, dur, vel=0.5):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 1.2) * np.where(t < dur, 1, np.exp(-(t - dur) * 20))
    return x * env * vel


def shaker(vel=0.15, seed=0):
    n = int(0.09 * SR)
    rng = np.random.default_rng(seed)
    x = highpass(rng.uniform(-1, 1, n), 5000)
    t = np.arange(n) / SR
    return x * np.exp(-t * 60) * vel


def make_bgm(duck_from=None):
    L = np.zeros((N, 2))
    seed = 0

    def put(sig, t, g, pan=0.0):
        i = int(t * SR)
        j = min(N, i + len(sig))
        if i < N:
            L[i:j, 0] += sig[:j - i] * g * math.cos((pan + 1) * math.pi / 4)
            L[i:j, 1] += sig[:j - i] * g * math.sin((pan + 1) * math.pi / 4)

    for b, name in enumerate(PROG):
        t0 = b * BAR
        root, tones = CHORDS[name]
        sec = 'intro' if b < 4 else 'chase' if b < 8 else 'harbor' if b < 14 else 'sunset' if b < 17 else 'end'
        # ギターのアルペジオ
        if sec != 'end' or b == 17:
            pat = [0, 1, 2, 3, 4, 3, 2, 1]
            for k, ix in enumerate(pat):
                if sec == 'end' and k > 0:
                    break
                tt = t0 + k * BEAT / 2
                d = BEAT * (0.6 if sec == 'chase' else 1.4)
                seed += 1
                put(pluck(mtof(tones[ix]), d, 0.22 if sec != 'chase' else 0.26, seed), tt, 1.0, -0.35)
        # ピアノの和音
        if sec in ('intro', 'harbor', 'sunset', 'end'):
            for m in tones[1:4]:
                put(piano(mtof(m + 12 if sec == 'sunset' else m), BAR * (2 if sec == 'end' else 0.95), 0.10), t0, 1.0, 0.3)
        # ベース
        if sec == 'chase':
            for k in range(4):
                put(bass(mtof(root + (12 if k % 2 else 0)), BEAT * 0.45, 0.35), t0 + k * BEAT, 1.0)
            for k in range(8):
                seed += 1
                put(shaker(0.10 if k % 2 else 0.05, seed), t0 + k * BEAT / 2, 1.0, 0.4)
        elif sec != 'end' or b == 17:
            put(bass(mtof(root), BAR * (0.95 if sec != 'end' else 2.5), 0.3), t0, 1.0)
        # メロディ
        for beat, m, d in MELODY.get(b, []):
            put(piano(mtof(m), d * BEAT * 0.95, 0.22 if sec != 'chase' else 0.2), t0 + beat * BEAT, 1.0, 0.1)
    # フェードアウト
    t = np.arange(N) / SR
    L *= np.clip((59.6 - t) / 3.0, 0, 1)[:, None]
    L /= np.max(np.abs(L)) + 1e-9
    L *= 0.8
    # セリフ中は少し下げる（ダッキング）
    if duck_from is not None:
        env = np.abs(duck_from)
        k = int(0.25 * SR)
        env = np.convolve(env, np.ones(k) / k, mode='same')
        g = 1 - 0.45 * np.clip(env / 0.05, 0, 1)
        L *= g[:, None]
    return L


# ---------------------------------------------------------------- 効果音


def pon(strength=1.0, seed=0):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    f = 520 * np.exp(-t * 14) + 230
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(seed)
    x = np.sin(ph) * np.exp(-t * 28) + 0.25 * lowpass(rng.uniform(-1, 1, n), 1500) * np.exp(-t * 60)
    return x * strength


def kotsun():
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 900 * t) + 0.6 * np.sin(2 * np.pi * 2150 * t)) * np.exp(-t * 45)
    return x * 0.8


def step(seed=0):
    n = int(0.07 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    return lowpass(rng.uniform(-1, 1, n), 700) * np.exp(-t * 70) * 1.2


def ambience(seed, fc, mod_hz, depth):
    rng = np.random.default_rng(seed)
    x = lowpass(rng.uniform(-1, 1, N), fc)
    x /= np.max(np.abs(x)) + 1e-9
    t = np.arange(N) / SR
    return x * (1 - depth + depth * 0.5 * (1 + np.sin(2 * np.pi * mod_hz * t + seed)))


def make_se():
    import scenes
    se = np.zeros(N)
    for i, (t, v) in enumerate(scenes.all_hits()):
        place(se, pon(0.35 + 0.65 * v, i), t, 0.9)
    place(se, kotsun(), scenes.S06.start + scenes.S06.STOP, 1.0)
    # 足音（S04・S05 走り）
    s4, s5 = scenes.S04(), scenes.S05()
    for cls, xfun, k in ((s4, lambda t: s4.haru_x(t), 0.034), (s5, lambda t: -160 + (t - s5.HSTART) * 760, 0.032)):
        prev = None
        for i in range(int(cls.dur * 200)):
            t = i / 200
            if cls is s5 and t < s5.HSTART:
                continue
            s = math.sin(xfun(t) * k)
            if prev is not None and (prev < 0) != (s < 0):
                place(se, step(i), cls.start + t, 0.35)
            prev = s
    t = np.arange(N) / SR
    # 風（朝）と波（港）
    wind = ambience(1, 400, 0.15, 0.6) * np.clip(1 - np.abs(t - 7) / 8, 0, 1) * 0.06
    waves = ambience(2, 900, 0.2, 0.7) * (np.clip((t - 25.5) * 2, 0, 1) * np.clip((60 - t) / 4, 0, 1)) * 0.12
    se = se + wind + waves
    return se


def main():
    os.makedirs(OUT, exist_ok=True)
    vpath = os.path.join(OUT, 'voice.wav')
    if os.environ.get('KEEP_VOICE') == '1' and os.path.exists(vpath):
        # 録音した本番の声を使う（voice_timing.json は手で合わせる）
        print('voice: keep', vpath)
        with wave.open(vpath) as w:
            raw = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768
            raw = raw.reshape(-1, w.getnchannels()).mean(axis=1)
        voice = np.zeros(N)
        voice[:min(N, len(raw))] = raw[:N]
    else:
        print('voice...')
        voice, _ = make_voice()
    print('bgm...')
    write_wav(os.path.join(OUT, 'bgm.wav'), make_bgm(voice))
    print('se...')
    write_wav(os.path.join(OUT, 'se.wav'), make_se() * 0.7)
    print('done')


if __name__ == '__main__':
    main()
