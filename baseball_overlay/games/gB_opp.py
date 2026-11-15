import os
import sys
W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telolib as T
NAMES = {"中田隼人": "中田 隼人", "多田幸之助": "多田 幸之助", "松平悠希": "松平 悠希", "二宮福久寿": "二宮 福久寿"}
RES = {"左2": "左二塁打"}
L = [("中田隼人", "サードエラー", "14:25"), ("多田幸之助", "レフトフライ", "16:08"), ("松平悠希", "中ヒット", "25:30"),
     ("二宮福久寿", "ファーストゴロ", "37:56"), ("中田隼人", "ピッチャーゴロ", "40:50"), ("多田幸之助", "中ヒット", "48:51"),
     ("松平悠希", "三振", "50:45"), ("二宮福久寿", "中ヒット", "53:46"), ("中田隼人", "四球", "1:06:37"),
     ("多田幸之助", "左2", "1:09:35"), ("松平悠希", "中ヒット", "1:11:32"), ("二宮福久寿", "四球", "1:17:56"),
     ("中田隼人", "四球", "1:22:20"), ("多田幸之助", "ショートゴロ", "1:25:55"), ("松平悠希", "四球", "1:28:51")]
cnt, prev = {}, {}
with open(W + "gB/opp/times.txt", "w") as f:
    for i, (n, r, ts) in enumerate(L):
        cnt[n] = cnt.get(n, 0) + 1
        p = [int(x) for x in ts.split(":")]
        t = p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]
        pos = {"中田隼人": "二", "多田幸之助": "捕" if t >= 2559 else "投", "松平悠希": "一", "二宮福久寿": "中"}.get(n)
        T.batter_png(0, NAMES[n], pos, 0, [], W + f"gB/opp/o{i:02d}.png", label="中田ジャパン",
                     sub=f"第{cnt[n]}打席" + ("　" + "・".join(prev[n]) if prev.get(n) else ""))
        prev.setdefault(n, []).append(RES.get(r, r))
        f.write(f"opp/o{i:02d} {t} 7\n")
