"""2026-11-21 長津少年野球大会 土居北 1-8 八幡浜（川之江野球場）。パワプロ風(pop)。顔写真なし。
映像は 00008.MTS + 00009.MTS、2回裏から。秒は結合後の時刻。
python3 games/g1121.py → $OVERLAY_WORK/g1121/ に一式。encode_game.sh で焼き込み。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import pop_style as P
import telolib as T
from style_kit import Kit

W = os.environ.get("OVERLAY_WORK", HERE + "/")
D = W + "g1121/"
AWAY, HOME = "土居北", "八幡浜"

# (開始秒, 終了秒, 回, top/bottom/final, 土居北, 八幡浜)  得点は1点ずつ入った時刻で区切る
STATES = [(0, 292, 2, "bottom", 0, 3), (292, 662, 3, "top", 0, 3), (662, 738, 3, "top", 1, 3),
          (738, 1022, 3, "bottom", 1, 3), (1022, 1366, 4, "top", 1, 3), (1366, 1683, 4, "bottom", 1, 3),
          (1683, 1790, 4, "bottom", 1, 4), (1790, 2222, 5, "top", 1, 4), (2222, 2698, 5, "bottom", 1, 4),
          (2698, 2830, 5, "bottom", 1, 5), (2830, 2924, 5, "bottom", 1, 6), (2924, 2941, 5, "bottom", 1, 7),
          (2941, 2988, 5, "bottom", 1, 8), (2988, 3340, 6, "top", 1, 8), (3340, 99999, 6, "final", 1, 8)]

DEF = {"投": "濱田り", "捕": "堀口", "一": "矢野", "二": "橋本ぎ", "三": "浜本る", "遊": "橋本す",
       "左": "野島", "中": "森こ", "右": "石堂ひ"}
DEF_T = 305  # 3回表の守備につくところ

# (秒, 打順, 選手キー, 守備, 第何打席, それまでの結果)
PAS = [(9, 8, "森こ", "中", 1, []), (78, 9, "野島", "左", 1, []), (196, 1, "矢野", "一", 2, ["三失"]),
       (786, 2, "浜本る", "三", 2, ["四球"]), (876, 3, "濱田り", "投", 2, ["右安"]), (958, 4, "堀口", "捕", 2, ["投飛"]),
       (1398, 5, "橋本す", "遊", 2, ["投ゴロ"]), (1436, 6, "橋本ぎ", "二", 2, ["中安"]),
       (1566, 7, "石堂ひ", "右", 2, ["投ゴロ"]), (1690, 8, "森こ", "中", 2, ["三飛"]), (1720, 9, "野島", "左", 2, ["三振"]),
       (2296, 1, "矢野", "一", 3, ["三失", "遊ゴロ"]), (2362, 2, "浜本る", "三", 3, ["四球", "遊飛"]),
       (2504, 3, "濱田り", "投", 3, ["右安", "一ゴロ"]), (2654, 4, "堀口", "捕", 3, ["投飛", "遊飛"]),
       (2708, 5, "橋本す", "遊", 3, ["投ゴロ", "中二"]), (2842, 6, "橋本ぎ", "二", 3, ["中安", "投ゴロ"]),
       (2950, 7, "石堂ひ", "右", 3, ["投ゴロ", "右安"])]

os.makedirs(D + "sb", exist_ok=True); os.makedirs(D + "bat", exist_ok=True)
with open(D + "states.txt", "w") as f:
    for i, (a, b, inn, half, aw, hm) in enumerate(STATES, 1):
        f.write(f"{a} {b} {inn} {half} {aw} {hm}\n")
        P.scoreboard(inn, half, aw, hm, D + f"sb/s{i:02d}.png", AWAY=AWAY, HOME=HOME)
K = Kit("pop")
K.defense(D + "defense.png", HOME, {p: T.disp(n) for p, n in DEF.items()})
open(D + "defense_t.txt", "w").write(str(DEF_T))
with open(D + "bat/times.txt", "w") as f:
    for i, (t, o, n, p, k, pr) in enumerate(PAS):
        P.batter(o, T.POS[p], T.disp(n), f"第{k}打席" + ("　" + "・".join(pr) if pr else ""), D + f"bat/b{i:02d}.png", photo=False)
        f.write(f"{i:02d} {t}\n")
# 対戦カード（左に八幡浜）→ 7秒のフェード付き透過動画
K.matchup(D + "matchup.png", "長津少年野球大会", "後攻", HOME, "先攻", AWAY)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-loop", "1", "-framerate", "60000/1001", "-t", "7", "-i", D + "matchup.png",
                "-vf", "format=rgba,fade=in:st=0:d=0.4:alpha=1,fade=out:st=6.6:d=0.4:alpha=1", "-c:v", "qtrle", D + "telop.mov"], check=True)
print("ok", D)
