import os
import sys
W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telolib as T
NAMES = {"中田隼人": "中田 隼人", "多田幸之助": "多田 幸之助", "松平悠希": "松平 悠希", "二宮福久寿": "二宮 福久寿", "松井晶聖": "松井 晶聖"}
RES = {"左2": "左二塁打", "中2": "中二塁打", "中安": "中前安打"}
L = [("中田隼人", "投フライ", "3:10"), ("多田幸之助", "中フライ", "7:30"), ("松平悠希", "四球", "20:40"),
     ("二宮福久寿", "左2", "25:56"), ("松井晶聖", "四球", "26:53"), ("中田隼人", "四球", "39:08"),
     ("多田幸之助", "左2", "41:01"), ("二宮福久寿", "死球", "53:53"), ("松井晶聖", "四球", "54:44"),
     ("中田隼人", "投フライ", "59:19"), ("多田幸之助", "四球", "1:00:01"), ("松平悠希", "四球", "1:10:17"),
     ("二宮福久寿", "中安", "1:14:44"), ("中田隼人", "三飛", "1:21:15"), ("多田幸之助", "四球", "1:22:11"),
     ("松平悠希", "中2", "1:28:35")]
cnt = {}
prev = {}
with open(W + "gA/opp/times.txt", "w") as f:
    for i, (n, r, ts) in enumerate(L):
        cnt[n] = cnt.get(n, 0) + 1
        p = [int(x) for x in ts.split(":")]
        t = p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]
        pos = {"中田隼人": "投" if t >= 3812 else "遊", "多田幸之助": "捕", "松平悠希": "二", "二宮福久寿": "左"}.get(n)
        T.batter_png(0, NAMES[n], pos, 0, [], W + f"gA/opp/o{i:02d}.png", label="中田ジャパン",
                     sub=f"第{cnt[n]}打席" + ("　" + "・".join(prev.get(n, [])) if prev.get(n) else ""))
        prev.setdefault(n, []).append(RES.get(r, r))
        f.write(f"{i:02d} {t}\n")
print(open(W + "gA/opp/times.txt").read())
