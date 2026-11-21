"""2026-11-21 長津少年野球大会（川之江野球場） 立花ヤングスターズ 16-1 八幡浜。パワプロ風（pop テーマ）。
元動画: 00010.MTS + 00011.MTS（結合後の秒で記述）。
使い方: OVERLAY_WORK=<作業フォルダ>/ python3 games/gC.py
        bash encode_game.sh <作業>/gC out.mp4 00010.MTS 00011.MTS
"""
import os
import sys
import subprocess
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ.get("OVERLAY_WORK", HERE + "/")
sys.path.insert(0, HERE)
import telolib as T
import pop_style as P
from style_kit import Kit

T.FULL["竹中り"] = T.FULL["竹中"]
AWAY, HOME = "立花ヤングスターズ", "八幡浜"
K = Kit("pop")

# 攻守の切り替え（秒, 回, top/bottom/final）
HALVES = [(340, 1, "top"), (960, 1, "bottom"), (1340, 2, "top"), (1740, 2, "bottom"), (2085, 3, "top"),
          (2555, 3, "bottom"), (2955, 4, "top"), (3355, 4, "bottom"), (3645, 5, "top"), (4815, 5, "final")]
# 得点（秒, "away"/"home"）。走者の生還が映像で確認できたもの。確認できなかった分は攻撃終了時に加算
RUNS = [(536, "away"), (579, "away"), (658, "away"), (955, "away"), (955, "away"),
        (1247, "home"),
        (2550, "away"), (2550, "away"),
        (3136, "away"),
        (3785, "away"), (4124, "away"), (4219, "away")] + [(4810, "away")] * 5
END = 99999

# (開始秒, 打順, 選手キー, 守備位置 or "代打", 第何打席, それまでの結果)
PAS = [(970, 1, "橋本す", "投", 1, []), (1050, 2, "浜本る", "遊", 1, []), (1097, 3, "濱田り", "一", 1, []),
       (1168, 4, "堀口", "捕", 1, []), (1250, 5, "橋本ぎ", "三", 1, []),
       (1755, 6, "石堂ひ", "二", 1, []), (1890, 7, "森こ", "中", 1, []), (2062, 8, "山中", "右", 1, []),
       (2565, 9, "野島", "左", 1, []), (2612, 1, "橋本す", "投", 2, ["中飛"]), (2670, 2, "浜本る", "遊", 2, ["二ゴロ"]),
       (2717, 3, "濱田り", "一", 2, ["右安"]), (2843, 4, "堀口", "捕", 2, ["左安"]),
       (3362, 5, "橋本ぎ", "三", 2, ["二ゴロ"]), (3453, 6, "石堂ひ", "二", 2, ["投飛"]),
       (3531, 7, "森こ", "中", 2, ["三振"]), (3621, 8, "竹中り", "代打", 1, [])]
DEF0 = {"投": "橋本す", "捕": "堀口", "一": "濱田り", "二": "石堂ひ", "三": "橋本ぎ", "遊": "浜本る",
        "左": "野島", "中": "森こ", "右": "山中"}
DEF_T = 350
# 追加テロップ（画像名, 開始秒, 表示秒）
EXTRA = [("matchup", 28, 9), ("change1", 3652, 10)]


def states():
    out = []
    pts = sorted({h[0] for h in HALVES} | {t for t, _ in RUNS})
    for i, a in enumerate(pts):
        b = pts[i + 1] if i + 1 < len(pts) else END
        inn, half = [(n, h) for t, n, h in HALVES if t <= a][-1]
        aw = sum(1 for t, s in RUNS if t <= a and s == "away")
        hm = sum(1 for t, s in RUNS if t <= a and s == "home")
        out.append((a, b, inn, half, aw, hm))
    return out


if __name__ == "__main__":
    d = W + "gC/"
    for sub in ("sb", "bat"):
        os.makedirs(d + sub, exist_ok=True)
    ST = states()
    with open(d + "states.txt", "w") as f:
        for i, (a, b, inn, half, aw, hm) in enumerate(ST, 1):
            f.write(f"{a} {b} {inn} {half} {aw} {hm}\n")
            P.scoreboard(inn, half, aw, hm, d + f"sb/s{i:02d}.png", AWAY=AWAY, HOME=HOME)
    K.defense(d + "defense.png", HOME, {k: T.disp(v) for k, v in DEF0.items()})
    open(d + "defense_t.txt", "w").write(str(DEF_T))
    with open(d + "bat/times.txt", "w") as f:
        for i, (t, o, n, p, k, pr) in enumerate(PAS):
            sub = f"第{k}打席" + ("　" + "・".join(pr) if pr else "")
            P.batter(o, T.POS.get(p, p), T.disp(n), sub, d + f"bat/b{i:02d}.png")
            f.write(f"{i:02d} {t}\n")
    K.matchup(d + "matchup.png", "長津少年野球大会", "後攻", HOME, "先攻", AWAY)
    K.change(d + "change1.png", HOME, [("右", T.disp("山中"), T.disp("竹中り")), ("左", T.disp("野島"), T.disp("西宮"))])
    with open(d + "overlays.txt", "w") as f:
        for p, t, du in EXTRA:
            f.write(f"{p} {du} {t}\n")
    print("\n".join(" ".join(map(str, s)) for s in ST))
