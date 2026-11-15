import os
import sys, os
W = os.environ.get("OVERLAY_WORK", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telolib as T
d = W + "gA/extra/"; os.makedirs(d, exist_ok=True)
T.TEAM = "中田ジャパン"
T.defense_png(d + "e0.png", {"捕": "多田 幸之助", "左": "二宮 福久寿", "遊": "中田 隼人", "二": "松平 悠希"})
T.change_png([("投", "", "中田 隼人")], d + "e2.png")
T.TEAM = "八幡浜"
T.change_png([("右", "濱田は", "竹中"), ("投", "濱田り", "矢野"), ("一", "橋本ぎ", "濱田り"), ("遊", "矢野", "橋本ぎ")], d + "e1.png")
T.change_png([("投", "矢野", "浜本る"), ("三", "浜本る", "橋本ぎ"), ("遊", "橋本ぎ", "矢野")], d + "e3.png")
# (file, start, duration)
open(d + "times.txt", "w").write("e0 754 15\ne1 3136 10\ne2 3812 10\ne3 5141 10\n")
