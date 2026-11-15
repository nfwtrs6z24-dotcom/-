import os
import sys, os
W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telolib as T
d = W + "gB/extra/"; os.makedirs(d, exist_ok=True)
T.TEAM = "中田ジャパン"
T.defense_png(d + "e0.png", {"二": "中田 隼人", "投": "多田 幸之助", "一": "松平 悠希", "中": "二宮 福久寿"})
T.change_png([("投", "多田 幸之助", ""), ("捕", "", "多田 幸之助")], d + "e1.png")
T.TEAM = "八幡浜"
T.change_png([("捕", "堀口", "橋本ぎ"), ("投", "濱田り", "堀口"), ("一", "橋本ぎ", "濱田り")], d + "e2.png")
T.change_png([("三", "浜本る", "堀口"), ("投", "堀口", "浜本る")], d + "e3.png")
T.change_png([("投", "浜本る", "矢野"), ("三", "堀口", "浜本る"), ("遊", "矢野", "堀口")], d + "e4.png")
open(d + "times.txt", "w").write("e0 30 15\ne1 2559 10\ne2 3768 10\ne3 4487 10\ne4 5066 10\n")
